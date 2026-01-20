import json
import os
import uuid
import shutil
import re
import time
from datetime import datetime

# Configuration
SOURCE_DIR = r"c:\Users\Anna.YR.Chen\Projects\sales_agent\docs\da_instructions"
# LOCAL_ROOT and ONELAKE_ROOT correspond to the "Config" directory level
LOCAL_ROOT = r"c:\Users\Anna.YR.Chen\Projects\sales_agent\scripts\published"
ONELAKE_ROOT = r"C:\Users\Anna.YR.Chen\OneLake - Microsoft\apac-dp-poc2024\Sales POA Agent v1.LLMPlugin\Files\Config"
BACKUP_ROOT = r"c:\Users\Anna.YR.Chen\Projects\sales_agent\scripts\backups"

def load_file(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def save_json(path, data, delete_first=False):
    """Saves JSON. If delete_first is True, explicitly removes the file to trigger sync detection."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if delete_first and os.path.exists(path):
            os.remove(path)
            # print(f"  - Removed old {os.path.basename(path)}")
            time.sleep(1) # Give sync agent time to notice the deletion
            
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
            f.flush()
            os.fsync(f.fileno())
        print(f"  ✓ {os.path.relpath(path, start=os.path.dirname(os.path.dirname(path)))}")
    except Exception as e:
        print(f"  Error saving to {path}: {e}")
        raise e

def create_backup(target_roots):
    """Creates a timestamped backup of the current structure from all targets."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BACKUP_ROOT, f"backup_{timestamp}")
    
    print(f"Creating backup in {backup_dir}...")
    
    files_to_backup = [
        "publish_info.json",
        os.path.join("published", "stage_config.json"),
        os.path.join("published", "data-warehouse-DATAAGENT_WH", "datasource.json"),
        os.path.join("published", "data-warehouse-DATAAGENT_WH", "fewshots.json")
    ]
    
    for label, root in target_roots.items():
        if not os.path.exists(root):
            continue
            
        dest_base = os.path.join(backup_dir, label)
        for rel_path in files_to_backup:
            src = os.path.join(root, rel_path)
            if os.path.exists(src):
                dest = os.path.join(dest_base, rel_path)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)
                
    print("✓ Backup completed.")

def sync_instructions():
    print("Starting synchronization...")
    
    roots = {
        "local": LOCAL_ROOT,
        "onelake": ONELAKE_ROOT
    }

    # 1. Generate new content (In memory)
    agent_instr = load_file(os.path.join(SOURCE_DIR, "agent_instructions.md"))
    source_instr = load_file(os.path.join(SOURCE_DIR, "source_instructions.md"))
    source_desc = load_file(os.path.join(SOURCE_DIR, "source_description.md")).strip()
    examples_json = load_file(os.path.join(SOURCE_DIR, "example_queries.json"))
    examples = json.loads(examples_json) if examples_json else {}

    # 2. Backup existing files
    create_backup(roots)

    # Prepare common version info
    current_v = datetime.now().strftime("%y%m%d_%H%M")

    for label, root in roots.items():
        print(f"\nSyncing to {label} target: {root}...")
        
        # OneLake target uses "Delete then Add" pattern to force sync trigger
        force_sync = (label == "onelake")
        
        # 3. Process publish_info.json
        p_info_path = os.path.join(root, "publish_info.json")
        p_info_content = load_file(p_info_path)
        if p_info_content:
            publish_info = json.loads(p_info_content)
            desc = publish_info.get("description", "")
            # Replace version string pattern
            new_desc = re.sub(r"-- v\d{6}(_\d{4})?\s*$", f"-- v{current_v} ", desc)
            publish_info["description"] = new_desc
            save_json(p_info_path, publish_info, delete_first=force_sync)

        # 4. Process stage_config.json
        published_dir = os.path.join(root, "published")
        sc_path = os.path.join(published_dir, "stage_config.json")
        sc_content = load_file(sc_path)
        if sc_content:
            stage_config = json.loads(sc_content)
            stage_config["aiInstructions"] = agent_instr
            save_json(sc_path, stage_config, delete_first=force_sync)

        # 5. Process datasource.json & fewshots.json
        wh_dir = os.path.join(published_dir, "data-warehouse-DATAAGENT_WH")
        
        ds_path = os.path.join(wh_dir, "datasource.json")
        ds_content = load_file(ds_path)
        if ds_content:
            datasource = json.loads(ds_content)
            datasource["dataSourceInstructions"] = source_instr
            datasource["userDescription"] = source_desc
            save_json(ds_path, datasource, delete_first=force_sync)

        fs_path = os.path.join(wh_dir, "fewshots.json")
        fs_content = load_file(fs_path)
        if fs_content:
            fewshots_data = json.loads(fs_content)
            existing_map = {item["question"]: item["id"] for item in fewshots_data.get("fewShots", [])}
            
            new_fewshots = []
            for question, query in examples.items():
                shot_id = existing_map.get(question, str(uuid.uuid4()))
                new_fewshots.append({
                    "id": shot_id,
                    "question": question,
                    "query": query
                })
            
            fewshots_data["fewShots"] = new_fewshots
            save_json(fs_path, fewshots_data, delete_first=force_sync)

    print("\nSynchronization completed successfully.")

if __name__ == "__main__":
    sync_instructions()
