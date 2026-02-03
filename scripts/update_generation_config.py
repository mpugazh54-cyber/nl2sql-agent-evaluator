import json
import os

CONFIG_PATH = 'data/qa/generation_config.json'
SAMPLE_FILES = [
    'data/sample/sample_data_billing.txt',
    'data/sample/sample_data_booking.txt'
]

def parse_sample_file(filepath):
    data = {}
    if not os.path.exists(filepath):
        print(f"Warning: File not found {filepath}")
        return data
        
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' not in line:
                continue
            key, val_str = line.split(':', 1)
            key = key.strip()
            # Split by comma, strip whitespace, and filter out empty strings or placeholders
            values = [v.strip() for v in val_str.split(',') if v.strip()]
            
            # Filter out generic placeholders if needed, though usually we want all unique values
            cleaned_values = []
            for v in values:
                if v in ['[Column not found]', '[No data]']:
                    continue
                cleaned_values.append(v)
            
            if key in data:
                data[key].extend(cleaned_values)
            else:
                data[key] = cleaned_values
    return data

def update_config():
    # Load existing config
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Collect all new values
    all_new_values = {}
    for sample_file in SAMPLE_FILES:
        file_data = parse_sample_file(sample_file)
        for key, values in file_data.items():
            if key not in all_new_values:
                all_new_values[key] = set()
            all_new_values[key].update(values)

    # Update config.dimensions
    dimensions = config.get('dimensions', {})
    updated_count = 0
    
    for dim_key, dim_vals in dimensions.items():
        if dim_key in all_new_values:
            current_set = set(dim_vals)
            new_set = all_new_values[dim_key]
            
            # Combine
            combined_set = current_set.union(new_set)
            
            # Update if changed
            if len(combined_set) > len(current_set):
                print(f"Updating {dim_key}: {len(current_set)} -> {len(combined_set)} values")
                # Sort for stability
                dimensions[dim_key] = sorted(list(combined_set))
                updated_count += 1
            else:
                 # Even if count is same, list might be different if we just want to ensure everything in sample is in config
                 # But usually set union covers it. 
                 pass

    config['dimensions'] = dimensions

    # Write back
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully updated {updated_count} dimensions in {CONFIG_PATH}")

if __name__ == '__main__':
    update_config()
