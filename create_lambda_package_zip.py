# create_lambda_package_zip.py
import zipfile
import os

def create_zip_package(source_folder, output_zip_path, lambda_file_name='lambda_function.py'):
    # Ensure the lambda_function.py is directly in the root of the zip
    # and all other libs are in their folders
    
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the lambda_function.py to the root of the zip
        lambda_file_path = os.path.join(source_folder, lambda_file_name)
        if os.path.exists(lambda_file_path):
            zipf.write(lambda_file_path, arcname=lambda_file_name)
        else:
            print(f"Warning: {lambda_file_path} not found. Ensure lambda_function.py is in the {source_folder} folder.")
            # If not found, perhaps it was created in the root of lambda_package
            # Let's try to add it from source_folder root if it's there
            if os.path.exists(os.path.join(os.path.dirname(source_folder), lambda_file_name)):
                 zipf.write(os.path.join(os.path.dirname(source_folder), lambda_file_name), arcname=lambda_file_name)


        # Add all other files/folders from source_folder
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                full_path = os.path.join(root, file)
                # Only add if it's not the lambda_file_name directly in the root, to avoid duplication
                if not (root == source_folder and file == lambda_file_name):
                    arcname = os.path.relpath(full_path, source_folder)
                    zipf.write(full_path, arcname)
    print(f"Successfully created {output_zip_path}")


if __name__ == "__main__":
    source_folder = 'lambda_package'
    output_zip_path = 'lambda_deployment_package.zip'
    create_zip_package(source_folder, output_zip_path)

    # Verify zip size
    zip_size_mb = os.path.getsize(output_zip_path) / (1024 * 1024)
    print(f"Zip file size: {zip_size_mb:.2f} MB")
    if zip_size_mb > 250:
        print("WARNING: Unzipped size might exceed Lambda's 250MB limit.")
    elif zip_size_mb > 50:
        print("NOTE: Zip file is >50MB. It must be uploaded to S3 first, then referenced by Lambda.")
    else:
        print("Zip file size is within direct upload limits (if unzipped size also fits).")