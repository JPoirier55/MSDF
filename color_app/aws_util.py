import boto3
from pathlib import Path
import os


def s3_upload(fileurl, filename):
    s3 = boto3.client('s3')
    path = Path(os.getcwd())
    bucket_name = 'image-proc-repo-kayla'
    s3.upload_file(str(path.parent) + fileurl, bucket_name, filename)


if __name__ == '__main__':
    s3_upload('\\media\\bird.png', 'birdypoo.png')