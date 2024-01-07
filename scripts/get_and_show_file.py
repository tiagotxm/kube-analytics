import urllib.request
import gzip


def download_and_show_file(url):

    filename, _ = urllib.request.urlretrieve(url)

    with gzip.open(filename, 'rt') as gz_file:
        content = gz_file.read()
    return content


def show_file(content):
    print(content)


if __name__ == "__main__":
    url = "https://ifood-data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz "

    content_file = download_and_show_file(url)
    show_file(content=content_file)
