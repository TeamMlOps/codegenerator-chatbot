import ollama

inp = input("Enter name for file: ")
prompt = '''Please generate a Terraform script that creates an AWS VPC and launches an EC2 instance in a public subnet.

Outputs: Displays EC2 instance ID and public IP address.
Add variables.tf content as well.
Do not include extra text. Give only HCL script.'''

response = ollama.chat(
    model="codellama",
    messages=[
        {
            "role": "user",
            "content": prompt,
        },
    ],
)

# Access the content in response dictionary
hcl_script = response["message"]["content"]

# Clean the script content
hcl_script = hcl_script.replace("```=hcl", "").replace("```", "").replace("terraform","")

# Define the output file
output_file = f"main_{inp}.tf"

# Write the cleaned script to a file
with open(output_file, "w", encoding="utf-8") as file_out:
    file_out.write(hcl_script)

print(f"\nTerraform script saved as {output_file}")
