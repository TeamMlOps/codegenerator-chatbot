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
region=input("Enter a region :")
cidr=input("Enter cidr range for vpc :")
public_cidr=input("Enter cidr range for public subnet :")
private_cidr=input("Enter cidr range for private subnet :")
AMI_ID=input("Enter AMI_ID :")
instance_type=input("Enter instance type:")

# Modified prompt to exclude unnecessary introductory text
prompt = f'''
Please generate a Terraform script that creates an AWS VPC and launches an EC2 instance in a public subnet.

region: region is {region}
VPC: Creates a VPC with a CIDR of {cidr}.
Subnets: Creates a public subnet {public_cidr} and a private subnet {private_cidr}.
Internet Gateway: Attach an internet gateway for public subnet internet access.
NAT Gateway: Configured in the public subnet for private subnet outbound internet access.
Route Tables: One for the public subnet (routes to the internet gateway) and one for the private subnet (routes to the NAT gateway).
Security Group: Allows SSH access on port 22 from any IP address.
EC2 Instance: Launches an EC2 instance in the public subnet using the provided {AMI_ID} , {instance_type}, and key pair my-key-pair.
Outputs: Displays the EC2 instance ID and its public IP address
Add variables.tf
Disclaimer:do not add extra introductory text and symbols also do not add operators like (```) and terraform or bash commands.
'''
# (ami-0c55b159cbfafe1f0)
# Initialize an empty buffer to store the entire output
full_output = ""

# Use the client to get the streamed response
for message in client.chat_completion(
    model=model_name,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=3500,  # Adjust token limit as needed
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
        

    # if "output" in line:
    #     resources_started = False
    #     main_started = False
    #     variables_started = False
    #     # output_started = True

    
    # Append lines to respective sections
    if main_started:
        main_content += line + "\n"
    elif variables_started:
        variables_content += line + "\n"
    elif resources_started:
        resources_content += line + "\n"
    # elif output_started:
    #     output_content += line + "\n"

# Specify file names for each section
main_file = f"main_{inp}.tf"
variables_file = f"variables_{inp}.tf"
resources_file = f"resources_{inp}.tf"
# output_file = f"output_{inp}.tf"


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


print(f"\nTerraform files have been saved as {main_file}, {variables_file}, {resources_file}")
