import React from 'react';

/**
 * Results display component.
 * Shows comprehensive evaluation results including scores, skills, and explanation.
 */
const ResultsDisplay = ({ results }) => {
  if (!results) return null;

  const {
    fit_score,
    semantic_similarity_score,
    matched_skills,
    missing_skills,
    experience_match_score,
    explanation
  } = results;

  // Determine score color based on fit score
  const getScoreColor = (score) => {
    if (score >= 75) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score) => {
    if (score >= 75) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent Fit';
    if (score >= 75) return 'Strong Fit';
    if (score >= 60) return 'Moderate Fit';
    if (score >= 40) return 'Weak Fit';
    return 'Poor Fit';
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Evaluation Results</h2>

      {/* Overall Fit Score */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-800">Overall Fit Score</h3>
          <span className={`text-3xl font-bold ${getScoreColor(fit_score)}`}>
            {fit_score.toFixed(1)}%
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className={`h-4 rounded-full transition-all duration-500 ${getScoreBgColor(fit_score)}`}
            style={{ width: `${fit_score}%` }}
          ></div>
        </div>
        
        <p className="mt-2 text-sm text-gray-600 font-medium">
          {getScoreLabel(fit_score)}
        </p>
      </div>

      {/* Component Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-900 mb-1">Semantic Similarity</h4>
          <p className="text-2xl font-bold text-blue-700">
            {(semantic_similarity_score * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-blue-600 mt-1">Conceptual alignment with job requirements</p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
          <h4 className="text-sm font-semibold text-purple-900 mb-1">Experience Match</h4>
          <p className="text-2xl font-bold text-purple-700">
            {(experience_match_score * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-purple-600 mt-1">Years of experience alignment</p>
        </div>
      </div>

      {/* Matched Skills */}
      {matched_skills.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <svg className="h-5 w-5 text-green-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Matched Skills ({matched_skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {matched_skills.map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium border border-green-300"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {missing_skills.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <svg className="h-5 w-5 text-red-600 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Missing Skills ({missing_skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {missing_skills.map((skill, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium border border-red-300"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Explanation */}
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">Analysis Summary</h3>
        <p className="text-sm text-gray-700 leading-relaxed">{explanation}</p>
      </div>
    </div>
  );
};

export default ResultsDisplay;