# import csv
# import re

# # Function to extract details from description using regex
# def extract_details(description):
#     clockspeed = turbo_speed = cores = threads = tdp = tdp_up = 'N/A'

#     # Regex patterns to find relevant information
#     clockspeed_pattern = re.search(r'Clockspeed: ([\d.]+ GHz)', description)
#     turbo_speed_pattern = re.search(r'Turbo Speed: ([\d.]+ GHz)', description)
#     cores_pattern = re.search(r'Cores: (\d+)', description)
#     threads_pattern = re.search(r'Threads: (\d+)', description)
#     tdp_pattern = re.search(r'TDP: ([\d.]+ W)', description)
#     tdp_up_pattern = re.search(r'TDP UP: ([\d.]+ W)', description)

#     # Extract values if patterns are found
#     if clockspeed_pattern:
#         clockspeed = clockspeed_pattern.group(1)
#     if turbo_speed_pattern:
#         turbo_speed = turbo_speed_pattern.group(1)
#     if cores_pattern:
#         cores = cores_pattern.group(1)
#     if threads_pattern:
#         threads = threads_pattern.group(1)
#     if tdp_pattern:
#         tdp = tdp_pattern.group(1)
#     if tdp_up_pattern:
#         tdp_up = tdp_up_pattern.group(1)

#     return clockspeed, turbo_speed, cores, threads, tdp, tdp_up


# def Execute(input_file,output_file):
#     # Read the original CSV and process it
#     input_file = input_file
#     output_file = output_file

#     with open(input_file, 'r', encoding='utf-8') as csvfile:
#         reader = csv.DictReader(csvfile)
        
#         # Create a new file to store the extracted information
#         with open(output_file, 'w', newline='', encoding='utf-8') as new_csvfile:
#             fieldnames = ['Processor', 'Clockspeed', 'Turbo Speed', 'Cores', 'Threads', 'TDP', 'TDP UP']
#             writer = csv.DictWriter(new_csvfile, fieldnames=fieldnames)
#             writer.writeheader()

#             for row in reader:
#                 processor = row['Processor']
#                 description = row['Description']

#                 # Extract details from the description
#                 clockspeed, turbo_speed, cores, threads, tdp, tdp_up = extract_details(description)

#                 # Write the processed row into the new CSV file
#                 writer.writerow({
#                     'Processor': processor,
#                     'Clockspeed': clockspeed,
#                     'Turbo Speed': turbo_speed,
#                     'Cores': cores,
#                     'Threads': threads,
#                     'TDP': tdp,
#                     'TDP UP': tdp_up
#                 })

#     print(f"Data has been processed and saved to {output_file}.")



# Execute('Final Year Project/cpu_details.csv','Final Year Project/cpu_details_processed.csv')



import csv
import re

# Function to extract details from description using regex
def extract_details(description):
    clockspeed = turbo_speed = cores = threads = tdp = tdp_up = 'N/A'

    # Regex patterns to find relevant information
    clockspeed_pattern = re.search(r'Clockspeed: ([\d.]+ GHz)', description)
    turbo_speed_pattern = re.search(r'Turbo Speed: ([\d.]+ GHz)', description)
    cores_pattern = re.search(r'Cores: (\d+)', description)
    threads_pattern = re.search(r'Threads: (\d+)', description)
    tdp_pattern = re.search(r'TDP: ([\d.]+ W)', description)
    tdp_up_pattern = re.search(r'TDP UP: ([\d.]+ W)', description)

    # Extract values if patterns are found
    if clockspeed_pattern:
        clockspeed = clockspeed_pattern.group(1)
    if turbo_speed_pattern:
        turbo_speed = turbo_speed_pattern.group(1)
    if cores_pattern:
        cores = cores_pattern.group(1)
    if threads_pattern:
        threads = threads_pattern.group(1)
    if tdp_pattern:
        tdp = tdp_pattern.group(1)
    if tdp_up_pattern:
        tdp_up = tdp_up_pattern.group(1)

    return clockspeed, turbo_speed, cores, threads, tdp, tdp_up

def extract_processor_name(processor):
    # Extract processor name using regex (before the first '(')
    match = re.match(r'([^(]+)', processor)
    return match.group(1).strip() if match else processor

def Execute(input_file, output_file):
    # Read the original CSV and process it
    with open(input_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        # Create a new file to store the extracted information
        with open(output_file, 'w', newline='', encoding='utf-8') as new_csvfile:
            fieldnames = ['Processor', 'Clockspeed', 'Turbo Speed', 'Cores', 'Threads', 'TDP', 'TDP UP']
            writer = csv.DictWriter(new_csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                processor = row['Processor']
                description = row['Description']

                # Extract the processor name
                processor_name = extract_processor_name(processor)

                # Extract details from the description
                clockspeed, turbo_speed, cores, threads, tdp, tdp_up = extract_details(description)

                # Write the processed row into the new CSV file
                writer.writerow({
                    'Processor': processor_name,
                    'Clockspeed': clockspeed,
                    'Turbo Speed': turbo_speed,
                    'Cores': cores,
                    'Threads': threads,
                    'TDP': tdp,
                    'TDP UP': tdp_up
                })

    print(f"Data has been processed and saved to {output_file}.")

# Execute the function
Execute('Final Year Project/cpu_details.csv', 'Final Year Project/cpu_details_processed.csv')
