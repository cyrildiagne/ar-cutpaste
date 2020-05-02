# AR Cut & Paste

An AR+ML prototype that allows cutting elements from your surroundings and pasting them in an image editing software.

Although only Photoshop is being handled currently, it may handle different outputs in the future.

⚠️ This is a research prototype and not a consumer / photoshop user tool.

## Modules

This prototype runs as 3 independent modules:

- **The mobile app**

  - Check out the [/app](/app) folder for instructions on how to deploy the app to your mobile.

- **The local server**

  - The interface between the mobile app and Photoshop.
  - It finds the position pointed on screen by the camera using [screenpoint](https://github.com/cyrildiagne/screenpoint)
  - Check out the [/server](/server) folder for instructions on configuring the local server

- **The object detection / background removal service**

  - For now, the salience detection and background removal are delegated to an external service
  - It would be a lot simpler to use something like [DeepLap](https://github.com/shaqian/tflite-react-native) directly within the mobile app. But that hasn't been implemented in this repo yet.

## Usage

### 1 - Configure Photoshop

- Go to "Preferences > Plug-ins", enable "Remote Connection" and set a friendly password that you'll need later.

<!--
### 2) Setup the local server

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
``` -->

### 2 - Setup the external salience object detection service

- As mentioned above, for the time being, you must deploy the
BASNet model (Qin & al, CVPR 2019) as an external HTTP service using this [BASNet-HTTP wrapper](https://github.com/cyrildiagne/basnet-http) (requires a CUDA GPU)

- You will need the deployed service URL to configure the local server

### 3 - Configure and run the local server

- Follow the instructions in [/server](/server) to setup & run the local server.

### 4 - Configure and run the mobile app

- Follow the instructions in [/app](/app) to setup & deploy the mobile app.

## Thanks and Acknowledgements

- [BASNet code](https://github.com/NathanUA/BASNet) for '[*BASNet: Boundary-Aware Salient Object Detection*](http://openaccess.thecvf.com/content_CVPR_2019/html/Qin_BASNet_Boundary-Aware_Salient_Object_Detection_CVPR_2019_paper.html) [code](https://github.com/NathanUA/BASNet)', [Xuebin Qin](https://webdocs.cs.ualberta.ca/~xuebin/), [Zichen Zhang](https://webdocs.cs.ualberta.ca/~zichen2/), [Chenyang Huang](https://chenyangh.com/), [Chao Gao](https://cgao3.github.io/), [Masood Dehghan](https://sites.google.com/view/masoodd) and [Martin Jagersand](https://webdocs.cs.ualberta.ca/~jag/)
- RunwayML for the [Photoshop paste code](https://github.com/runwayml/RunwayML-for-Photoshop/blob/master/host/index.jsx)
