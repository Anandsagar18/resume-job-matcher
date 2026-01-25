import axios from 'axios';

const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * API service for communicating with the FastAPI backend.
 * Handles resume-job fit evaluation requests.
 */
class APIService {
  /**
   * Evaluate resume-job fit by sending PDF and job description to backend.
   * 
   * @param {File} resumeFile - PDF file object from file input
   * @param {string} jobDescription - Job description text
   * @returns {Promise<Object>} Evaluation results containing fit score, skills, etc.
   * @throws {Error} API errors with user-friendly messages
   */
  async evaluateResumeFit(resumeFile, jobDescription) {
    try {
      // Create FormData to send multipart/form-data request
      const formData = new FormData();
      formData.append('resume', resumeFile);
      formData.append('job_description', jobDescription);

      // Send POST request to /evaluate endpoint
      const response = await axios.post(
        `${API_BASE_URL}/evaluate`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          // Timeout after 60 seconds (ML model can take time on first run)
          timeout: 60000,
        }
      );

      return response.data;
    } catch (error) {
      // Handle different error scenarios with user-friendly messages
      if (error.response) {
        // Server responded with error status
        const detail = error.response.data?.detail || 'Server error occurred';
        throw new Error(detail);
      } else if (error.request) {
        // Request made but no response received
        throw new Error('Unable to reach the server. Please ensure the backend is running on http://localhost:8000');
      } else {
        // Error setting up the request
        throw new Error('Failed to send request: ' + error.message);
      }
    }
  }

  /**
   * Check if the backend API is healthy and ready.
   * 
   * @returns {Promise<Object>} Health status object
   */
  async checkHealth() {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`, {
        timeout: 5000,
      });
      return response.data;
    } catch (error) {
      throw new Error('Backend health check failed');
    }
  }
}

export default new APIService();