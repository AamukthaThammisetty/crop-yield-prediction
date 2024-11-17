'use client'

import React, { useEffect, useState } from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardFooter, CardContent } from '@/components/ui/card';
import { MapPin, Loader2, Divide, Loader } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import axios from 'axios';
import { MultiSelect } from "@/components/ui/multi-select";

const CropYieldPrediction = () => {
  const [formData, setFormData] = useState({
    Item: '',
    fertilizer_type: '',
    fertilizer_amount: '',
    pesticide_type: '',
    pesticides_tonnes: '',
    country: ''
  });

  const [location, setLocation] = useState({
    latitude: null,
    longitude: null,
    error: null,
    loading: false
  });

  const [prediction, setPrediction] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [suggestionGeneration, setSuggestionsGenerating] = useState(false);
  const [fertilizerTypes, setFertilizerTypes] = useState(["Nitrogen", "Phosphorus", "Potassium", "Organic", "Compound"]);
  const [pesticideTypes, setPesticideTypes] = useState<string[]>(["Insecticide", "Herbicide", "Fungicide", "Rodenticide"]);
  const [selectedPesticides, setSelectedPesticides] = useState<string[]>([]);
  const [selectedFertilizers, setSelectedFertilizers] = useState<string[]>([]);

  const [error, setError] = useState(null);

  // const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>(["react", "angular"]);
  // const frameworksList = [
  //   { value: "react", label: "React" },
  //   { value: "angular", label: "Angular" },
  //   { value: "vue", label: "Vue" },
  //   { value: "svelte", label: "Svelte" },
  //   { value: "ember", label: "Ember" },
  // ];


  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear previous predictions and errors when form changes
    setPrediction(null);
    setSuggestions(null);
    setError(null);
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
          // @ts-ignore
          setLocation({
            latitude: null,
            longitude: null,
            // @ts-ignore
            error: "An unknown error occurred.",
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

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      // Create FormData object
      const submitData = new FormData();

      // Add form fields to FormData
      submitData.append('Item', formData.Item);
      submitData.append('fertilizer_type', formData.fertilizer_type);
      submitData.append('fertilizer_amount', formData.fertilizer_amount);
      submitData.append('pesticide_type', formData.pesticide_type);
      submitData.append('pesticides_tonnes', formData.pesticides_tonnes);
      submitData.append('country', formData.country);

      // Add location data
      // @ts-ignore
      submitData.append('lat', location.latitude);
      // @ts-ignore
      submitData.append('lon', location.longitude);

      // Make prediction request
      const predictionResponse = await axios.post(
        'http://localhost:8080/api/predict',
        submitData,
        { withCredentials: true }
      );

      console.log(predictionResponse.data.data);
      document.getElementById('prediction-results')?.scrollIntoView({ behavior: 'smooth' });

      // Store prediction result
      setPrediction(predictionResponse.data.data);

      // Make suggestions request with prediction data
      setSuggestionsGenerating(true);
      setSuggestions(null);
      const suggestionsResponse = await axios.post(
        'http://localhost:8080/api/suggestions',
        {
          Item: formData.Item,
          Area: formData.country,
          predicted_yield: predictionResponse.data.data.predicted_yield,
          avg_temp: predictionResponse.data.data.avg_temp,
          average_rain_fall_mm_per_year: predictionResponse.data.data.average_rain_fall_mm_per_year,
          pesticide_type: formData.pesticide_type,
          fertilizer_type: formData.fertilizer_type
        },
        { withCredentials: true }
      );

      setSuggestionsGenerating(false);

      // Store suggestions
      setSuggestions(suggestionsResponse.data.data.suggestions);
      console.log(suggestionsResponse.data.data.suggestions);

    } catch (err) {
      //@ts-ignore
      setError(err.response?.data?.error || 'An error occurred while making the prediction');
      console.error('Error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const crops = [
    "Maize", "Potatoes", "Rice", "Sorghum", "Soybeans",
    "Wheat", "Cassava", "Sweet potatoes", "Plantains", "Yams"
  ];

  const cropData = {
    "Maize": {
      fertilizers: ["Urea", "Diammonium Phosphate", "Ammonium Nitrate", "Compound"],
      pesticides: ["Insecticide", "Herbicide", "Fungicide"]
    },
    "Potatoes": {
      fertilizers: ["Nitrogen", "Phosphorus", "Potassium", "Calcium Ammonium Nitrate"],
      pesticides: ["Fungicide", "Rodenticide", "Nematicide"]
    },
    "Rice, paddy": {
      fertilizers: ["Urea", "Superphosphate", "Muriate of Potash"],
      pesticides: ["Insecticide", "Herbicide", "Larvicide"]
    },
    "Sorghum": {
      fertilizers: ["Urea", "Phosphorus", "Organic", "Sulfur"],
      pesticides: ["Herbicide", "Bactericide", "Repellent"]
    },
    "Soybeans": {
      fertilizers: ["Potassium", "Organic", "Magnesium"],
      pesticides: ["Fungicide", "Insecticide", "Acaricide"]
    },
    "Wheat": {
      fertilizers: ["Nitrogen", "Phosphorus", "Potassium", "Diammonium Phosphate"],
      pesticides: ["Herbicide", "Fungicide", "Larvicide"]
    },
    "Cassava": {
      fertilizers: ["Phosphorus", "Potassium", "Organic"],
      pesticides: ["Insecticide", "Rodenticide", "Molluscicide"]
    },
    "Sweet potatoes": {
      fertilizers: ["Nitrogen", "Phosphorus", "Calcium Ammonium Nitrate"],
      pesticides: ["Fungicide", "Herbicide", "Nematicide"]
    },
    "Plantains and others": {
      fertilizers: ["Urea", "Organic", "Magnesium"],
      pesticides: ["Insecticide", "Larvicide", "Repellent"]
    },
    "Yams": {
      fertilizers: ["Nitrogen", "Potassium", "Sulfur"],
      pesticides: ["Fungicide", "Rodenticide", "Bactericide"]
    }
  };

  useEffect(() => {
    const item = formData['Item'];
    // @ts-ignore
    if (item && cropData[item]) {
      // @ts-ignore
      setFertilizerTypes(cropData[item].fertilizers || []);
      // @ts-ignore
      setPesticideTypes(cropData[item].pesticides || []);
    }
  }, [formData['Item']]);

  useEffect(() => {
    if (selectedFertilizers.length == 0) {
      formData['fertilizer_type'] = '';
    } else {
      formData['fertilizer_type'] = selectedFertilizers[0];
    }
  }, [selectedFertilizers]);

  useEffect(() => {
    if (selectedPesticides.length == 0) {
      formData['pesticide_type'] = '';
    } else {
      formData['pesticide_type'] = selectedPesticides[0];
    }
  }, [selectedFertilizers]);



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
              <iframe id="mapIframe" className="w-full h-72"
                src={`https://www.google.com/maps?q=${location.latitude},${location.longitude}&hl=es;z=14&output=embed`} ></iframe>
            </div>



            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Right Card */}
        <Card className="shadow-lg">
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-6 pt-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="Item">Crop Type</Label>
                  <Select
                    value={formData.Item}
                    onValueChange={(value) => handleInputChange('Item', value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a crop" />
                    </SelectTrigger>
                    <SelectContent>
                      {crops.map((crop) => (
                        <SelectItem key={crop} value={crop}>
                          {crop}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fertilizer_type">Fertilizer Type</Label>
                  <MultiSelect
                    options={fertilizerTypes}
                    onValueChange={setSelectedFertilizers}
                    defaultValue={selectedPesticides}
                    placeholder="Select Pesticides"
                    variant="inverted"
                    animation={2}
                    maxCount={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="fertilizer_amount">Fertilizer Amount (kg)</Label>
                  <Input
                    type="number"
                    value={formData.fertilizer_amount}
                    onChange={(e) => handleInputChange('fertilizer_amount', e.target.value)}
                    placeholder="Enter amount in kg"
                    className="w-full"
                  />
                </div>



                <div className="space-y-2">
                  <Label htmlFor="pesticide_type">Pesticide Type</Label>
                  <MultiSelect
                    options={pesticideTypes}
                    onValueChange={setSelectedFertilizers}
                    defaultValue={selectedPesticides}
                    placeholder="Select Pesticides"
                    variant="inverted"
                    animation={2}
                    maxCount={3}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pesticides_tonnes">Pesticides Amount (tonnes)</Label>
                  <Input
                    type="number"
                    value={formData.pesticides_tonnes}
                    onChange={(e) => handleInputChange('pesticides_tonnes', e.target.value)}
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
                      <SelectItem value="India">India</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>

            <CardFooter>
              <Button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700"
                disabled={isSubmitting || !location.latitude}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Predicting...
                  </>
                ) : (
                  'Predict Yield'
                )}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
      <div className='mt-20 ' id='prediction-results'>
        {/* Prediction Results */}
        {prediction && (
          <div className="mt-6 p-4 bg-green-50 rounded-lg">
            <h2 className="text-lg font-semibold text-green-800 mb-2">Prediction Results</h2>
            <div className="space-y-2 text-sm">
              <p><span className="font-medium">Predicted Yield:</span> {prediction.predicted_yield} hg/ha</p>
              {/* <p><span className="font-medium">Average Temperature:</span> {prediction.avg_temp}°C</p>
                  <p><span className="font-medium">Average Rainfall:</span> {prediction.average_rain_fall_mm_per_year} mm/year</p> */}
            </div>
          </div>
        )}

        {(isSubmitting && suggestionGeneration) || suggestions ? (
          <div className="mt-6 space-y-4">
            {(isSubmitting && suggestionGeneration) && (
              <div className="flex items-center justify-center h-96 w-full">
                <div className="flex items-center justify-center gap-2">
                  <Loader className="animate-spin" /> Generating Suggestions
                </div>
              </div>
            )}
            {/* Suggestions */}
            {suggestions && (
              <>
                <h2 className="text-lg font-semibold text-green-800">Improvement Suggestions</h2>
                {suggestions.map((suggestion: any, index: any) => (
                  <div key={index} className="p-4 bg-white rounded-lg shadow-sm border border-green-100">
                    <h3 className="font-medium text-green-700">{suggestion.category}</h3>
                    <p className="text-sm text-gray-600 mt-1">{suggestion.suggestion}</p>
                    <p className="text-xs text-gray-500 mt-1">{suggestion.reason}</p>
                  </div>
                ))}
              </>
            )}
          </div>
        ) : null}

      </div>
    </div>
  );
};

export default CropYieldPrediction;
