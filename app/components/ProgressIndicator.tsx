// @refresh reset

import React, { useState, useEffect } from "react";
import { View, Animated, StyleSheet } from "react-native";
import Svg, { Circle } from "react-native-svg";

const AnimatedCircle = Animated.createAnimatedComponent(Circle);

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
  },
});

function getInitialState() {
  const anim = new Animated.Value(0);
  const r1 = anim.interpolate({
    inputRange: [0, 1],
    outputRange: [5, 10],
  });
  return { anim, r1 };
}

export default function ProgressIndicator() {
  const [state, setState] = useState(getInitialState());

  useEffect(() => {
    const { anim } = state;
    Animated.timing(anim, {
      toValue: 1,
      duration: 1000,
      // useNativeDriver: true,
    }).start();
  }, []);

  // const cx = parseInt(fadeAnim * 25) + ''
  // console.log(fadeAnim)

  return (
    <View style={styles.container}>
      <Svg height="50%" width="100%" viewBox="0 0 100 100">
        <AnimatedCircle cx="25" cy="25" r={state.r1} fill="white" />
      </Svg>
    </View>
  );
}
