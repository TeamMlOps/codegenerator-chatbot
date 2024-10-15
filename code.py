from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Hugging Face Inference Client with the API key from .env
client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))

# Define the model and the prompt for generating the Terraform script
model_name = "meta-llama/Llama-3.2-3B-Instruct"
inp = input("Enter a service (for file name): ")

# Modified prompt to exclude unnecessary introductory text
prompt = '''
## Generate a complete Terraform script split into:
1. main.tf: Include the provider, VPC setup, and outputs.
2. variables.tf: Include all reusable variables such as VPC CIDR blocks, instance types.
3. resources.tf: Define all resources like subnets, security groups, EC2 instances.
Make sure to provide only the content without additional introductory text.
'''

# Initialize an empty buffer to store the entire output
full_output = ""

# Use the client to get the streamed response
for message in client.chat_completion(
    model=model_name,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2000,  # Adjust token limit as needed
    stream=True,  # Stream the output
):
    # Capture the streamed content
    content = message.choices[0].delta.content
    
    # Print to console (optional)
    print(content, end="")
    
    # Append the streamed content to the full output
    full_output += content

# After all the content is received, process and split into sections
main_content = ""
variables_content = ""
resources_content = ""

# Split the full_output based on logical keywords and assign to respective files
main_started = False
variables_started = False
resources_started = False

# Check each line of the output to decide where it belongs
for line in full_output.splitlines():
    line = line.strip()  # Clean leading and trailing spaces

    if "provider" in line or "output" in line:
        main_started = True
        variables_started = False
        resources_started = False
    
    if "variable" in line:
        variables_started = True
        main_started = False
        resources_started = False

    if "resource" in line:
        resources_started = True
        main_started = False
        variables_started = False
    
    # Append lines to respective sections
    if main_started:
        main_content += line + "\n"
    elif variables_started:
        variables_content += line + "\n"
    elif resources_started:
        resources_content += line + "\n"

# Specify file names for each section
main_file = f"main_{inp}.tf"
variables_file = f"variables_{inp}.tf"
resources_file = f"resources_{inp}.tf"

# Write the content to respective files, including the file name as a comment
with open(main_file, "w") as main_file_out:
    main_file_out.write("# File: main.tf\n\n")  # Add the comment
    main_file_out.write(main_content)

with open(variables_file, "w") as variables_file_out:
    variables_file_out.write("# File: variables.tf\n\n")  # Add the comment
    variables_file_out.write(variables_content)

with open(resources_file, "w") as resources_file_out:
    resources_file_out.write("# File: resources.tf\n\n")  # Add the comment
    resources_file_out.write(resources_content)

print(f"\nTerraform files have been saved as {main_file}, {variables_file}, and {resources_file}")
