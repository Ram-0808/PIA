import requests
import json
import threading
from TenderManagement.models import PDFExtraction
import os
from dotenv import load_dotenv

load_dotenv()
WORK_FLOW_URL = os.getenv('WORK_FLOW_URL',)
WORK_FLOW_API_KEY = os.getenv('WORK_FLOW_API_KEY')
print('WORK_FLOW_API_KEY', WORK_FLOW_API_KEY)
def upload_file(file_path, user):
    # upload_url = "http://20.197.5.172/v1/files/upload"
    upload_url = f"{WORK_FLOW_URL}/files/upload"
    print('upload_url',upload_url)

    headers = {
        "Authorization": f"Bearer {WORK_FLOW_API_KEY}",
        # "Authorization": "Bearer app-Z9LpDGXGOzMdvZ6ZEoNrMWL8",
    }
    
    try:
        print("Upload file...")
        with open(file_path, 'rb') as file:
            files = {
                'file': (file_path, file, "application/pdf")  # Make sure the file is uploaded with the appropriate MIME type
            }
            data = {
                "user": user,
                "type": "PDF", # "TXT"  # Set the file type to TXT
            }
            
            response = requests.post(upload_url, headers=headers, files=files, data=data)
            print('----------------------------------TEXT - JSON')
            print(response.text)
            print(response.json())
            print('----------------------------------')
            if response.status_code == 201:  # 201 means creation is successful
                print("File uploaded successfully")
                return response.json().get("id"),None  # Get the uploaded file ID
            else:
                print(f"File upload failed, status code: {response.status_code}")
                return None, f"File upload failed, status code: {response.status_code}"
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None, str(e)

def run_workflow(file_id, user, response_mode="blocking"):
    # workflow_url = "http://20.197.5.172/v1/workflows/run"
    workflow_url = f"{WORK_FLOW_URL}/workflows/run"
    print('workflow_url',workflow_url)
    headers = {

        # "Authorization": "Bearer app-Z9LpDGXGOzMdvZ6ZEoNrMWL8",
        "Authorization": f"Bearer {WORK_FLOW_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": {
            "pdf_doc": [{
                "transfer_method": "local_file",
                "upload_file_id": file_id,
                "type": "document"
            }],
            "sys_msg":"Extract all the pdf data"
        },
        "response_mode": response_mode,
        "user": user
    }

    try:
        print("Run Workflow...")
        response = requests.post(workflow_url, headers=headers, json=data)
        print('----------------------------------TEXT - JSON')
        print(response.text)
        print(response.json())
        print(json.dumps(response.json()))
        print('----------------------------------')
        if response.status_code == 200:
            print("Workflow execution successful")
            return response.text,None
        else:
            print(f"Workflow execution failed, status code: {response.status_code}")
            return None, f"status code: {response.status_code}"
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None, str(e)

# Usage Examples

# def fileextractor():
#     file_path = "./GeM-Bidding-6290961.pdf"
#     user = "difyuser"

#     # Upload files
#     file_id = upload_file(file_path, user)
#     if file_id:
#         # The file was uploaded successfully, and the workflow continues to run
#         result = run_workflow(file_id, user)
#         print(result)
#     else:
#         print("File upload failed and workflow cannot be executed")


# def fileextractor(file_path, user):
#     user = "spruceapp"
#     # Upload files
#     file_id, upload_error = upload_file(file_path, user)
#     if not file_id:
#         return {"status": "error", "message": f"File upload failed: {upload_error}"}

#     # Run workflow
#     workflow_result, workflow_error = run_workflow(file_id, user)
#     if workflow_result:
#         return {"status": "success", "data": workflow_result}
#     else:
#         return {"status": "error", "message": f"Workflow execution failed: {workflow_error}"}






class PDFExtractionThread(threading.Thread):
    def __init__(self, request_id ):
        self.status = 0
        self.request_id = request_id
        
        threading.Thread.__init__(self)

    def run(self):
        obj = PDFExtraction.objects.filter(
            id=self.request_id,
        ).first()
        
        print('obj',obj)

        if not obj:
            return None
        
        file_path = obj.file.path
        print('file_path',file_path,type(file_path))
        user = "spruceapp"
        file_id, upload_error = upload_file(file_path, user)
        # result = upload_file(file_path, user)
        # print('upload_file result:', result)
        # file_id, upload_error = result
        # file_id = result
        if not file_id:
            obj.extarct_data = f"File upload failed: {upload_error}"
            obj.status = 3
            obj.save()
        else:
            # Run workflow
            workflow_result, workflow_error = run_workflow(file_id, user)
            if workflow_result:
                obj.extarct_data = workflow_result
                obj.status = 2
                obj.save()
            else:
                obj.extarct_data = f"Workflow execution failed: {workflow_error}"
                obj.status = 3
                obj.save()


def start_extract_pdf( id):

    print(id)

    thread = PDFExtractionThread(id)
    thread.start()
