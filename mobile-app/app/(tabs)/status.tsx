import { Link } from "expo-router";
import { Text, View } from "react-native";

export default function Tab() {
  return (
    <View className="flex flex-col">
      <Text>Status</Text>
      <Link href="/report">Zgłoś problem</Link>
    </View>
  );
}
