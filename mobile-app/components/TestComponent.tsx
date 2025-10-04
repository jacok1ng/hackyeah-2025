import { Text, View } from "react-native";

export const TestComponent = () => {
  return (
    <View className="w-full flex-1 items-center justify-center  bg-blue-500 bg-fuchsia-50 text-red-50">
      <Text className="font-bold text-yellow-600">Hello World</Text>
      <Text className="text-purple-600">This is a test component</Text>
    </View>
  );
};
