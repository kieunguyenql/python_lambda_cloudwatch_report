import boto3
from datetime import date
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

########################################################### 

clw_client = boto3.client('cloudwatch')

############# get_metrics fuction #########################

def get_metrics(base_widget,image_name,image_title):
#    metrics_array = []
#    for instance_id in objects_list:
#        metric = base_widget.copy()
#        metric[0][3] = f"{instance_id}"
#        metrics_array.append(metric)

    widget = {
        "metrics": base_widget,
        "start": "-PT24H",
        "title": image_title,
        "timezone": "+0700"
    }
    widget_json = json.dumps(widget)

    response = clw_client.get_metric_widget_image(
        MetricWidget=widget_json,
        OutputFormat='png'
    )

    image_bytes = response['MetricWidgetImage']

    image_path = os.path.join('/tmp', image_name)
    
    with open(image_path, 'wb') as image_file:
        image_file.write(image_bytes)

#################### send email fuction ####################

def send_images_to_email(sender_email, sender_password, recipient_email, directory, message_content):
    # Set up the SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = 'Cloudwatch-monitoring-daily-report'
    
    # Attach the message content
    text_part = MIMEText(message_content, 'plain')
    message.attach(text_part)
    # Iterate over the files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            # Open the image file
            with open(os.path.join(directory, filename), 'rb') as file:
                # Create a MIMEImage object
                image = MIMEImage(file.read())
                image.add_header('Content-Disposition', 'attachment', filename=filename)
                message.attach(image)

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send the email
    server.send_message(message)
    server.quit()

############################################################
    
#if __name__ == "__main__":

def lambda_handler(event, context):
    
    today= date.today()
    today=str(today)
    email_message= f"Hello, this is report on {today}"
    
    get_metrics([
                 ["AWS/EC2", "CPUUtilization", "InstanceId", "i-05fb500020da1f407"],
                 ["AWS/EC2", "CPUUtilization", "InstanceId", "i-0c2e85b8d1cf4e34b"],
                 ["AWS/EC2", "CPUUtilization", "InstanceId", "i-06cd1b7d872bdbcc3"],
                 ["AWS/EC2", "CPUUtilization", "InstanceId", "i-02888059c729af05c"]
               ],
                "ec2-cpu.png", 
                "ec2-cpu"
                )
  
    get_metrics([
                 ["AWS/Kafka", "CpuUser", "Cluster Name", "kafka", "Broker ID", "3"], 
                 ["AWS/Kafka", "CpuUser", "Cluster Name", "kafka", "Broker ID", "2"], 
                 ["AWS/Kafka", "CpuUser", "Cluster Name", "kafka", "Broker ID", "1"]
                 ], 
                 "kafka-cpu-user.png", 
                 "kafka-cpu-user",
                )

    get_metrics([
                 ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "general-purpose-cache-001"], 
                 ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "general-purpose-cache-002"]
                 ], 
                 "elastic-cache-cpu.png", 
                 "elastic-cache-cpu",
                )

    get_metrics([
                 ["AWS/ES", "FreeStorageSpace", "ClientId", "501361391094", "DomainName", "general-purpose-production"], 
                 ["AWS/ES", "FreeStorageSpace", "ClientId", "501361391094", "DomainName", "production-service-log"]
                 ], 
                 "es-FreeStorageSpace.png", 
                 "es-FreeStorageSpace",
                )

    get_metrics([
                 ["AWS/ES", "JVMMemoryPressure", "ClientId", "501361391094", "DomainName", "general-purpose-production"], 
                 ["AWS/ES", "JVMMemoryPressure", "ClientId", "501361391094", "DomainName", "production-service-log"]
                 ], 
                 "es-JVMMemoryPressure.png", 
                 "es-JVMMemoryPressure",
                )

    print('Images are saved successfully.')
    

    print('Send email report')

    send_images_to_email('nguyen.van@ascendcorp.com', 'dlfxcspapykcwxxy', 'kieunguyen.ql@gmail.com', '/tmp', email_message)
