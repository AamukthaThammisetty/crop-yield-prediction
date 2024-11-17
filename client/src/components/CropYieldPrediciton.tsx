'use client'

import React, { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardFooter, CardContent } from '@/components/ui/card';
import { MapPin, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const CropYieldPrediction = () => {
  const [formData, setFormData] = useState({
    crop: '',
    fertilizerType: '',
    fertilizerAmount: '',
    pesticideType: '',
    pesticidesAmount: '',
    country: ''
  });

  const [location, setLocation] = useState({
    latitude: null,
    longitude: null,
    error: null,
    loading: false
  });

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getLocation = () => {
    setLocation(prev => ({ ...prev, loading: true, error: null }));

    if (navigator.geolocation) {

      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            // @ts-ignore
            latitude: position.coords.latitude,
            // @ts-ignore
            longitude: position.coords.longitude,
            error: null,
            loading: false
          });
        },
        (error) => {
          const errorMessages = {
            1: "Location access denied. Please enable location services.",
            2: "Location information unavailable.",
            3: "Location request timed out."
          };
          setLocation({
            latitude: null,
            longitude: null,
            // @ts-ignore
            error: errorMessages[error.code] || "An unknown error occurred.",
            loading: false
          });
        }
      );
    } else {
      // @ts-ignore
      setLocation(prev => ({
        ...prev,
        error: "Geolocation is not supported by this browser.",
        loading: false
      }));
    }
  };

  const handleSubmit = (e: any) => {
    e.preventDefault();
    // Add your prediction logic here
    console.log('Form submitted:', { ...formData, location });
  };

  const crops = [
    "Maize", "Potatoes", "Rice", "Sorghum", "Soybeans",
    "Wheat", "Cassava", "Sweet potatoes", "Plantains", "Yams"
  ];

  const fertilizerTypes = [
    "Nitrogen", "Phosphorus", "Potassium", "Organic", "Compound"
  ];

  const pesticideTypes = [
    "Insecticide", "Herbicide", "Fungicide", "Rodenticide"
  ];

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Card */}
        <Card className="shadow-lg">
          <CardHeader className="space-y-4">
            <div className="bg-gradient-to-r from-green-100 to-green-50 rounded-full w-20 h-20 mx-auto flex items-center justify-center">
              <MapPin className="w-10 h-10 text-green-600" />
            </div>
            <h1 className="text-2xl font-bold text-center text-gray-800">
              Crop Yield Prediction
            </h1>
          </CardHeader>

          <CardContent className="space-y-6">
            <div className="text-center space-y-4">
              {location.error && (
                <Alert variant="destructive">
                  <AlertDescription>{location.error}</AlertDescription>
                </Alert>
              )}

              {location.latitude && (
                <div className="text-sm text-gray-600 space-y-1">

                  <p>Latitude: {location.latitude}°</p>
                  <p>Longitude: {location.longitude}°</p>
                </div>
              )}

              <Button
                onClick={getLocation}
                className="w-full bg-green-600 hover:bg-green-700"
                disabled={location.loading}
              >
                {location.loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Getting Location...
                  </>
                ) : (
                  'Get Location'
                )}
              </Button>
            </div>

            <div className="w-full h-64 bg-gray-100 rounded-lg overflow-hidden">
              <iframe
                className="w-full h-full border-0"
                src={`https://www.google.com/maps?q=${location.latitude},${location.longitude}&hl=es;z=14&output=embed`}
                allowFullScreen
              />
            </div>
          </CardContent>
        </Card>

        {/* Right Card */}
        <Card className="shadow-lg">
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-6 pt-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="crop">Crop Type</Label>
                  <Select
                    value={formData.crop}
                    onValueChange={(value) => handleInputChange('crop', value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a crop" />
                    </SelectTrigger>
                    <SelectContent>
                      {crops.map((crop) => (
                        <SelectItem key={crop} value={crop.toLowerCase()}>
                          {crop}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fertilizerType">Fertilizer Type</Label>
                  <Select
                    value={formData.fertilizerType}
                    onValueChange={(value) => handleInputChange('fertilizerType', value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select fertilizer type" />
                    </SelectTrigger>
                    <SelectContent>
                      {fertilizerTypes.map((type) => (
                        <SelectItem key={type} value={type.toLowerCase()}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fertilizerAmount">Fertilizer Amount (kg)</Label>
                  <Input
                    type="number"
                    value={formData.fertilizerAmount}
                    onChange={(e) => handleInputChange('fertilizerAmount', e.target.value)}
                    placeholder="Enter amount in kg"
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pesticideType">Pesticide Type</Label>
                  <Select
                    value={formData.pesticideType}
                    onValueChange={(value) => handleInputChange('pesticideType', value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select pesticide type" />
                    </SelectTrigger>
                    <SelectContent>
                      {pesticideTypes.map((type) => (
                        <SelectItem key={type} value={type.toLowerCase()}>
                          {type}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pesticidesAmount">Pesticides Amount (tonnes)</Label>
                  <Input
                    type="number"
                    value={formData.pesticidesAmount}
                    onChange={(e) => handleInputChange('pesticidesAmount', e.target.value)}
                    placeholder="Enter amount in tonnes"
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="country">Country</Label>
                  <Select
                    value={formData.country}
                    onValueChange={(value) => handleInputChange('country', value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select your country" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="india">India</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>

            <CardFooter>
              <Button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700"
              >
                Predict Yield
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default CropYieldPrediction;
