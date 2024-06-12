# Cloud - Photo Album Setup
This guide explains how to set up a cloud-based photo album using AWS services including OpenSearch, Lambda, S3, API Gateway, and Lex.

Visit the following links for more information on setting up and managing the photo album project:

- For the S3 bucket setup, check out the repository [here](https://github.com/tanishabisht/Cloud-PhotoAlbumS3Pipeline).
- For details on the Lambda functions setup, visit the repository [here](https://github.com/tanishabisht/Cloud-PhotoAlbumLambdaPipeline).
- If you need more detailed steps and configurations, you can find them [here](/steps.md).


# Quick overview of the setup

![architecture](/architecture.png)

## 1. Set Up OpenSearch
**Create an OpenSearch Domain**: Name it `photos`.


## 2. Upload and Index Photos
- **Create S3 Bucket**: Name it `b2-imgs`.
- **Lambda Function for Indexing (LF1)**: Name it `index-photos`.
  - **Set Up Trigger**: Trigger LF1 when a photo is added to `b2-imgs`.
  - **Function Tasks**: When an image is uploaded:
    - Use AWS Rekognition to detect image labels.
    - Retrieve metadata from the image using S3 SDK’s headObject method.
    - Create and store a JSON array of labels in OpenSearch.
- **Permissions**: Ensure LF1 and OpenSearch can interact by sharing their IAM role ARNs.


## 3. Search Functionality
- **Lambda Function for Searching (LF2)**: Name it `search-photos`.
- **Set Up a Lex Bot**: Name it `search-bot` for handling search queries.
  - **Intents**: Create intents to capture one or two keywords from user queries for searching photos.
- **Permissions**: Same as step 2, ensure LF2 and OpenSearch can interact.


## 4. API Gateway
- **Create a REST API**: Import settings from a Swagger or Open API file.
- **Configure Methods**:
  - **PUT**: For uploading images to S3.
  - **GET**: For retrieving data from OpenSearch to display results.
- **Deploy API**: Create a new stage and generate an SDK for frontend integration.


## 5. Frontend Setup
- **Web Pages**:
  - **Index.html**: Main landing page.
  - **Gallery.html**: Search gallery using keywords.
  - **Upload.html**: Upload new images to the gallery.
- **Deploy on S3**: Upload these files to an S3 bucket named `photo-gallery-fe` and set it to allow public access.

## Technologies used
`aws` `lambda` `s3` `api-gateway` `rekognition` `lex` `opensearch`