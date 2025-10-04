import { Link } from "expo-router";
import { Text, View } from "react-native";

export default function Index() {
  return (
    <View className="flex-1 items-center justify-center bg-red-700">
      <Text>Edit app/index.tsx to edit this screen.</Text>
      <Link href="/(tabs)" className="text-blue-500">
        Go to Tabs
      </Link>
    </View>
  );
}
