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
region = input("Enter a region: ")
cidr = input("Enter CIDR range for VPC: ")
public_cidr = input("Enter CIDR range for public subnet: ")
private_cidr = input("Enter CIDR range for private subnet: ")
AMI_ID = input("Enter AMI ID: ")
instance_type = input("Enter instance type: ")

# Modified prompt
prompt = f'''
Please generate a Terraform script that creates an AWS VPC and launches an EC2 instance in a public subnet.

Region: {region}
VPC CIDR: {cidr}
Public Subnet CIDR: {public_cidr}
Private Subnet CIDR: {private_cidr}
EC2 AMI: {AMI_ID}
Instance Type: {instance_type}

Outputs: Displays EC2 instance ID and public IP address.
Add variables.tf content as well.
Do not include extra text.Give only HCL script.
'''
# AMI_ID=ami-08718895af4dfa033
# Initialize an empty buffer to store the entire output
full_output = ""

# Use the client to get the streamed response
for message in client.chat_completion(
    model=model_name,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=3500,  # Adjust token limit as needed
    stream=True,  # Stream the output
):
    content = message.choices[0].delta.content
    print(content, end="")
    full_output += content

# Save everything to a single file
output_file = f"main_{inp}.tf"
with open(output_file, "w") as file_out:
    file_out.write(full_output)

print(f"\nTerraform script saved as {output_file}")
