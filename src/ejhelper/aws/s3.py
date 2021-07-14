import boto3
from retry import retry
import json
import decimal

from ejhelper.helper.logging import getLogger

logger = getLogger(__name__)

class S3:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self.bucket_name)
        self.objects = self.bucket.objects

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def Object(self, key):
        return self.bucket.Object(key)

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def upload_file(
            self,
            file_path,
            key,
            ExtraArgs=None,
            Callback=None,
            Config=None):
        return self.bucket.upload_file(file_path, key)

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def put_fileobj(
            self,
            fileobj,
            key,
            ExtraArgs=None,
            Callback=None,
            Config=None):
        return self.put(fileobj, key)

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def upload_fileobj(
            self,
            fileobj,
            key,
            ExtraArgs=None,
            Callback=None,
            Config=None):
        return self.bucket.upload_fileobj(fileobj, key)

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def put_object(
            self,
            key,
            data,
            ExtraArgs=None,
            Callback=None,
            Config=None):
        return self.bucket.put_object(
            Key=key, Body=json.dumps(
                data, cls=DecimalEncoder))

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def download_file(self, key, file_path):
        return self.bucket.download_file(key, file_path)

    @retry(tries=3, delay=1, backoff=1, logger=logger)
    def head_object(self, key, **kwargs):
        """
        ヘッダー情報取得

        response sample

        {
        'AcceptRanges': 'bytes',
        'ContentLength': 71352,
        'ContentType': 'binary/octet-stream',
        'ETag': '"6dc2578a1487ea1ed7...665781a0"',
        'LastModified': datetime.datetime(20...o=tzutc()),
        'Metadata': {
        },
        'ResponseMetadata': {
            'HTTPHeaders': {
            ...
            },
            'HTTPStatusCode': 200,
            'HostId': 'XH+GK5Oq9HGU54VtmfK...lt+9RcLU=',
            'RequestId': 'E32D331143CF3C12',
            'RetryAttempts': 0
        }
        }
        """
        result = None
        try:
            result = self.s3.meta.client.head_object(
                Bucket=self.bucket_name, Key=key, **kwargs)
        except Exception as e:
            logger.debug(e.args)
            result = None
        return result



class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def decimalEncoder(o):
    if isinstance(o, decimal.Decimal):
        if o % 1 > 0:
            return float(o)
        else:
            return int(o)
    return o
