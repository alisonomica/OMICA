# Installation of Docker for DeepVariant

DeepVariant official [tutorials](https://cloud.google.com/life-sciences/docs/tutorials/deepvariant)

Make sure that older versions of Docker are removed and install Docker Container (for Ubuntu) by repository
```
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

Install docker
```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

List the docker version available for your repo
```
apt-cache madison docker-ce
```

Install a specific version using the version string from the second column, for example, 5:18.09.1~3-0~ubuntu-xenial instead of <VERSION_STRING>
```
sudo apt-get install docker-ce=<VERSION_STRING> docker-ce-cli=<VERSION_STRING> containerd.io
```

Verify the installation is successful
```
sudo docker run hello-world
```


