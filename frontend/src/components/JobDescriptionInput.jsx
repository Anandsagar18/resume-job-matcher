import React from 'react';

/**
 * Job description text input component.
 * Multi-line textarea for entering job requirements.
 */
const JobDescriptionInput = ({ value, onChange, error }) => {
  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Job Description <span className="text-red-500">*</span>
      </label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste the job description here... Include requirements, responsibilities, and desired skills."
        rows={10}
        className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
          error 
            ? 'border-red-300 focus:ring-red-500 focus:border-red-500' 
            : 'border-gray-300 focus:ring-primary-500 focus:border-primary-500'
        }`}
      />
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
      <p className="mt-2 text-xs text-gray-500">
        Enter the complete job description including required skills, experience, and responsibilities.
      </p>
    </div>
  );
};

export default JobDescriptionInput;