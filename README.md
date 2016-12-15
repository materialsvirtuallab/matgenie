materialsvirtuallab.org
=======================

This repo contains the Django code for the main www.materialsvirtuallab.org
website. The website is run off Heroku with static assets being served from Amazon Web Services S3.

Recommended setup
-----------------

There are actually two repos - this Github repo, where you do most of the coding, including branching, etc. for new features, and the heroku repo, where you push to for production deployment. Note that you always need to push to heroku to actually deploy the actual website. Simply pushing to Github alone has no effect on the production site. The instructions below provides a means to push to both repos at once. This assumes you already set up your heroku credentials properly.

First, clone this Github repo by doing the following:

    git clone git@github.com:materialsvirtuallab/materialsvirtuallab.org.git

Let's add a "all" remote that allows you to push to both the Github and the heroku repos at once.

    git remote add all git@github.com:materialsvirtuallab/materialsvirtuallab.org.git
    git remote set-url --add all git@heroku.com:materialsvirtuallab.git

With the above, you can now do:

    git push all --all

to push to both the Github and Heroku repos.

Static assets
-------------

We use Amazon S3 to host the static assets (pictures, 
etc.) which may be large and inefficient to hold on Heroku. To update the 
static assets, you need to install the Amazon CLI (http://aws.amazon.com/cli/)
and set up the access and secret keys. 
Pls first ask Prof. Ong to create an AWS Access Key ID and Secret Key for you. 
Then set up AWS configuration
    
    aws configure
    
    AWS Access Key ID [None]: AWSAccessKeyId
    AWS Secret Access Key [None]: AWSSecretKey 
    Default region name [None]: us-west-1 
    Default output format [None]: 
  
From the root folder, then run::

    aws s3 sync materialsvirtuallab/static s3://mavrl-web/static --acl public-read
