## BUILD-DEPLOY PROCESS

It is generic guide serves as overview. Please see per project setup to run
ansible part below.

There is a jenkins job to build. See Jenkinsfile.BUILD for more info. This
build and push the zip file to XVT AWS S3 public bucket.

To deploy per project there is an ansible role `ecs_auto_scale_lambda` which
will take the artifact in above s3 bucket and setup the lambda to use it. It
will save to a `per project` bucket and use that for lambda rather than pointing
all lambda to the same public repo.

Any new development pushed to master will be build automatically and save to XVT
Public repo S3 bucket.

To update per project:

- Check the build for the `VERSION` value and confirm it is what you want
- Update ansible inventory data to use that version
- Run the corresponding playbook where it calls the ansible role.

## Maintenance

In the build log it prints out the artifacts saved in XVT puiblic repo bucket.
If it is too many Admin need to cleanup manually if required.
