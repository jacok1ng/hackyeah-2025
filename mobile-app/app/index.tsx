import { Redirect } from "expo-router";
import { Pressable, View } from "react-native";

export default function Index() {
  return (
    <View className="flex-1 items-center justify-center bg-red-700">
      <Redirect href="/(tabs)" />
    </View>
  );
}
