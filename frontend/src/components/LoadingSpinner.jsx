import React from 'react';

/**
 * Loading spinner component displayed during API requests.
 * Shows an animated spinner with status message.
 */
const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className="h-16 w-16 rounded-full border-4 border-gray-200"></div>
        <div className="absolute top-0 left-0 h-16 w-16 rounded-full border-4 border-primary-500 border-t-transparent animate-spin"></div>
      </div>
      <p className="mt-4 text-gray-600 font-medium">
        Analyzing resume and job description...
      </p>
      <p className="mt-2 text-sm text-gray-500">
        This may take a few seconds
      </p>
    </div>
  );
};

export default LoadingSpinner;