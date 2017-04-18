#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DATE=`date +%Y%m%d_%H%M%S`

S3_BUCKET=com.artify.selstagram.server

if [ -n "$1" ]
    then
        ENVIRONMENT_NAME=$1
else
    ENVIRONMENT_NAME=webserver-staging
fi

if [[ ${ENVIRONMENT_NAME} == *"worker"* ]];
    then
        EBEXTENSION=.ebextensions.worker
else
    EBEXTENSION=.ebextensions.webserver
fi


echo "environment name = ${ENVIRONMENT_NAME}, ebextension = ${EBEXTENSION}"

if [ -n "$2" ]
    then
        VERSION=$2
else
    VERSION=0.0.1
fi

echo "version = ${VERSION}"


cd ${DIR}/selstagram2

eb use ${ENVIRONMENT_NAME}


BUNDLE=../webserver_${DATE}.zip
S3_KEY=webserver_${DATE}.zip

rm -rf ./.ebextensions && cp -R ${DIR}/${EBEXTENSION} .ebextensions && \
zip ${BUNDLE}  -r * .ebextensions .elasticbeanstalk && \
rm -rf ./.ebextensions && \
aws s3 cp ${BUNDLE} s3://${S3_BUCKET}/ && \
aws elasticbeanstalk create-application-version \
    --process \
    --application-name selstagram \
    --version-label ${ENVIRONMENT_NAME}-${VERSION} \
    --source-bundle S3Bucket=${S3_BUCKET},S3Key=${S3_KEY} \
&&
eb deploy --version ${VERSION}

cd -

#aws elasticbeanstalk compose-environments \
#    --application-name selstagram \
#    --group-name ${GROUP_NAME} \
#    --version-labels worker-${WORKER_VERSION} web-${WEB_VERSION}