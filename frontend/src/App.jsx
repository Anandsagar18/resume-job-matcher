import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResultsDisplay from './components/ResultsDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import apiService from './services/api';

/**
 * Main application component.
 * Orchestrates the resume-job fit evaluation workflow.
 */
function App() {
  // Form state
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  
  // Validation errors
  const [fileError, setFileError] = useState(null);
  const [jobDescError, setJobDescError] = useState(null);

  /**
   * Handle file upload with validation.
   */
  const handleFileChange = (file, error) => {
    setResumeFile(file);
    setFileError(error);
    // Clear results when file changes
    if (file) {
      setResults(null);
      setError(null);
    }
  };

  /**
   * Handle job description input.
   */
  const handleJobDescriptionChange = (value) => {
    setJobDescription(value);
    setJobDescError(null);
    // Clear results when job description changes
    if (value) {
      setResults(null);
      setError(null);
    }
  };

  /**
   * Validate form before submission.
   */
  const validateForm = () => {
    let isValid = true;

    if (!resumeFile) {
      setFileError('Please upload a resume PDF');
      isValid = false;
    }

    if (!jobDescription.trim()) {
      setJobDescError('Please enter a job description');
      isValid = false;
    }

    return isValid;
  };

  /**
   * Handle form submission and API call.
   */
  const handleEvaluate = async () => {
    // Clear previous errors and results
    setError(null);
    setResults(null);

    // Validate form
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Call API service
      const evaluationResults = await apiService.evaluateResumeFit(
        resumeFile,
        jobDescription
      );

      // Display results
      setResults(evaluationResults);
      
      // Scroll to results
      setTimeout(() => {
        document.getElementById('results-section')?.scrollIntoView({ 
          behavior: 'smooth',
          block: 'start'
        });
      }, 100);

    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Reset form to initial state.
   */
  const handleReset = () => {
    setResumeFile(null);
    setJobDescription('');
    setResults(null);
    setError(null);
    setFileError(null);
    setJobDescError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            AI Resume-Job Fit Scorer
          </h1>
          <p className="mt-2 text-gray-600">
            Upload your resume and job description to get an intelligent fit analysis powered by machine learning
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Error Display */}
        <ErrorMessage 
          message={error} 
          onDismiss={() => setError(null)} 
        />

        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Upload Information</h2>

          <FileUpload
            file={resumeFile}
            onFileChange={handleFileChange}
            error={fileError}
          />

          <JobDescriptionInput
            value={jobDescription}
            onChange={handleJobDescriptionChange}
            error={jobDescError}
          />

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={handleEvaluate}
              disabled={loading}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800'
              }`}
            >
              {loading ? 'Evaluating...' : 'Evaluate Fit'}
            </button>

            <button
              onClick={handleReset}
              disabled={loading}
              className="px-6 py-3 rounded-lg font-semibold text-gray-700 bg-gray-200 hover:bg-gray-300 active:bg-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
            <LoadingSpinner />
          </div>
        )}

        {/* Results Display */}
        <div id="results-section">
          {results && <ResultsDisplay results={results} />}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <p className="text-center text-sm text-gray-600">
            Built with React, Tailwind CSS, and FastAPI • ML-powered semantic analysis
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;