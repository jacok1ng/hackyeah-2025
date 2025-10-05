import { BackArrowIcon } from "@/assets/icons/BackArrowIcon";
import { BellIcon } from "@/assets/icons/BellIcon";
import { useRouter } from "expo-router";
import { View, Text, Pressable } from "react-native";

interface HeaderProps {
  title: string;
}

const Header = ({ title }: HeaderProps) => {
  const router = useRouter();

  return (
    <View className="h-[110px] flex-row items-center bg-white px-6 pb-3 pt-[60px]">
      {router.canGoBack() ? (
        <Pressable
          className="w-1/4 flex-row justify-start"
          onPress={() => router.back()}
        >
          <BackArrowIcon color="#FBC535" />
        </Pressable>
      ) : (
        <View className="w-1/4 flex-row justify-start"></View>
      )}

      <View className="w-2/4 items-center">
        <Text className="text-[18px] font-bold">{title}</Text>
      </View>
      <View className="w-1/4 flex-row justify-end">
        <BellIcon />
      </View>
    </View>
  );
};

export default Header;
