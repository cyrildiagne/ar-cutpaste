import React, { useState, useEffect } from "react";
import {
  Text,
  View,
  Image,
  TouchableWithoutFeedback,
  StyleSheet,
} from "react-native";
import * as ImageManipulator from "expo-image-manipulator";
import { Camera } from "expo-camera";

// import ProgressIndicator from "./components/ProgressIndicator";
import server from "./components/Server";

const styles = StyleSheet.create({
  resultImgView: {
    position: "absolute",
    zIndex: 200,
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
  },
  resultImg: {
    position: "absolute",
    zIndex: 300,
    top: "25%",
    left: 0,
    width: "100%",
    height: "50%",
  },
});

interface State {
  hasPermission: boolean;
  type: any;
  camera: any;
  currImgSrc: string | null;
}

export default function App() {
  const [state, setState] = useState({
    hasPermission: false,
    type: Camera.Constants.Type.back,
    camera: null,
    currImgSrc: "",
  } as State);

  const [pressed, setPressed] = useState(false);

  let camera: any = null;

  useEffect(() => {
    (async () => {
      // Ping the server on startup.
      server.ping();
      // Request permission.
      const { status } = await Camera.requestPermissionsAsync();
      const hasPermission = status === "granted" ? true : false;
      setState({ ...state, hasPermission });
    })();
  }, []);

  async function cut(): Promise<string> {
    const start = Date.now();
    console.log("");
    console.log("Cut");

    console.log("> taking image...");
    // const opts = { skipProcessing: true, exif: false };
    const opts = {};
    let photo = await camera.takePictureAsync(opts);

    console.log("> resizing...");
    const { uri } = await ImageManipulator.manipulateAsync(
      photo.uri,
      [
        { resize: { width: 256, height: 512 } },
        { crop: { originX: 0, originY: 128, width: 256, height: 256 } },
      ]
      // { compress: 0, format: ImageManipulator.SaveFormat.JPEG, base64: false }
    );

    console.log("> sending to /cut...");
    const resp = await server.cut(uri);

    console.log(`Done in ${((Date.now() - start) / 1000).toFixed(3)}s`);
    return resp;
  }

  async function paste() {
    const start = Date.now();
    console.log("");
    console.log("Paste");

    console.log("> taking image...");
    // const opts = { skipProcessing: true, exif: false };
    const opts = {};
    let photo = await camera.takePictureAsync(opts);

    console.log("> resizing...");
    const { uri } = await ImageManipulator.manipulateAsync(photo.uri, [
      { resize: { width: 512, height: 1024 } },
    ]);

    console.log("> sending to /paste...");
    try {
      const resp = await server.paste(uri);
      if (resp.status !== "ok") {
        throw new Error(resp)
      }
    } catch(e) {
      console.error('error pasting:', e);
    }

    console.log(`Done in ${((Date.now() - start) / 1000).toFixed(3)}s`);
  }

  async function onPressIn() {
    setPressed(true);

    const resp = await cut();
    setState({ ...state, currImgSrc: resp });
  }

  async function onPressOut() {
    setPressed(false);
    if (state.currImgSrc) {
      await paste();
      setState({ ...state, currImgSrc: null });
    }
  }

  if (state.hasPermission === null) {
    return <View />;
  }
  if (state.hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={{ flex: 1 }}>
      <Camera
        style={{ flex: 1 }}
        type={state.type}
        ratio="2:1"
        ref={(ref) => (camera = ref)}
      >
        <TouchableWithoutFeedback onPressIn={onPressIn} onPressOut={onPressOut}>
          <View
            style={{
              flex: 1,
              backgroundColor: "transparent",
              flexDirection: "row",
            }}
          ></View>
        </TouchableWithoutFeedback>
      </Camera>

      {pressed && state.currImgSrc !== "" ? (
        <>
          <View pointerEvents="none" style={styles.resultImgView}>
            <Image
              style={styles.resultImg}
              source={{ uri: state.currImgSrc }}
              resizeMode="stretch"
            />
          </View>
        </>
      ) : null}

      {/* <ProgressIndicator /> */}
    </View>
  );
}
