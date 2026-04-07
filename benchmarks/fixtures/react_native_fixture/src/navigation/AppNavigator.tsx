import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import { Routes } from './Routes';
import { HomeScreen } from '../screens/HomeScreen';
import { DetailsScreen } from '../screens/DetailsScreen';

const Stack = createNativeStackNavigator();

export function AppNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name={Routes.Home} component={HomeScreen} />
      <Stack.Screen name={Routes.Details} component={DetailsScreen} />
    </Stack.Navigator>
  );
}
