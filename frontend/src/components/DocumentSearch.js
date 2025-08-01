import React, { useState } from 'react';

function DocumentSearch() {
    const [searchType, setSearchType] = useState('semantic'); // 'semantic' or 'keyword'
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [selectedDoc, setSelectedDoc] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        setLoading(true);
        setError(null);
        try {
            const endpoint = searchType === 'semantic' 
                ? `/search/?query=${encodeURIComponent(searchQuery)}`
                : `/keyword-search/?keyword=${encodeURIComponent(searchQuery)}`;
            
            const response = await fetch(`http://localhost:8000${endpoint}`);
            if (!response.ok) throw new Error('Search failed');
            const data = await response.json();
            setSearchResults(data.results);
        } catch (err) {
            setError('Failed to perform search');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const fetchDocumentDetails = async (docId) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://localhost:8000/get-document/${docId}`);
            if (!response.ok) throw new Error('Failed to fetch document');
            const data = await response.json();
            setSelectedDoc(data);
        } catch (err) {
            setError('Failed to fetch document details');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const renderSearchResult = (result) => {
        const commonElements = (
            <>
                <div className="font-medium text-indigo-600">
                    {result.filename}
                </div>
                <div className="text-sm text-gray-500">
                    Type: {result.document_type}
                </div>
            </>
        );

        return (
            <div
                key={result.doc_id}
                className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                onClick={() => fetchDocumentDetails(result.doc_id)}
            >
                {commonElements}
                
                {/* Score for semantic search */}
                {searchType === 'semantic' && typeof result.score === 'number' && (
                    <div className="text-sm text-gray-400">
                        Score: {result.score.toFixed(3)}
                    </div>
                )}

                {/* Matches for keyword search */}
                {searchType === 'keyword' && result.matches && (
                    <div className="mt-2">
                        {result.matches.map((match, idx) => (
                            <div key={idx} className="text-sm text-gray-600 mb-1 p-2 bg-yellow-50 rounded">
                                ...{match}...
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="bg-white shadow-lg rounded-xl p-6 transition-all duration-300 hover:shadow-xl">
            {/* Search Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-indigo-100 rounded-lg">
                    <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <h2 className="text-2xl font-bold text-slate-800">Document Search</h2>
            </div>

            {/* Search Type Toggle */}
            <div className="flex gap-4 mb-6">
                <button
                    onClick={() => setSearchType('semantic')}
                    className={`px-4 py-2 rounded-lg ${
                        searchType === 'semantic'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    } transition-colors duration-200`}
                >
                    Semantic Search
                </button>
                <button
                    onClick={() => setSearchType('keyword')}
                    className={`px-4 py-2 rounded-lg ${
                        searchType === 'keyword'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    } transition-colors duration-200`}
                >
                    Keyword Search
                </button>
            </div>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search documents..."
                        className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-indigo-500"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className={`px-6 py-2 rounded-lg bg-indigo-600 text-white font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors duration-200 ${
                            loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                    >
                        {loading ? 'Searching...' : 'Search'}
                    </button>
                </div>
            </form>

            {/* Error Message */}
            {error && (
                <div className="mb-4 p-4 bg-red-50 text-red-600 rounded-lg">
                    {error}
                </div>
            )}

            {/* Search Results */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Results List */}
                <div className="space-y-4">
                    <h3 className="font-semibold text-lg text-gray-700">Search Results</h3>
                    {searchResults.length === 0 ? (
                        <p className="text-gray-500">No results found</p>
                    ) : (
                        <div className="space-y-2">
                            {searchResults.map((result) => renderSearchResult(result))}
                        </div>
                    )}
                </div>

                {/* Document Details */}
                <div className="border-l pl-4">
                    <h3 className="font-semibold text-lg text-gray-700 mb-4">Document Details</h3>
                    {selectedDoc ? (
                        <div className="space-y-4">
                            <div>
                                <h4 className="font-medium text-gray-700">Document Type</h4>
                                <p className="text-gray-600">{selectedDoc.document_type}</p>
                            </div>
                            <div>
                                <h4 className="font-medium text-gray-700">Created At</h4>
                                <p className="text-gray-600">
                                    {new Date(selectedDoc.created_at).toLocaleString()}
                                </p>
                            </div>
                            <div>
                                <h4 className="font-medium text-gray-700">Content</h4>
                                <p className="text-gray-600 whitespace-pre-wrap max-h-96 overflow-y-auto">
                                    {selectedDoc.raw_text}
                                </p>
                            </div>
                            {selectedDoc.structured_data && Object.keys(selectedDoc.structured_data).length > 0 && (
                                <div>
                                    <h4 className="font-medium text-gray-700">Structured Data</h4>
                                    <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                                        {JSON.stringify(selectedDoc.structured_data, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p className="text-gray-500">Select a document to view details</p>
                    )}
                </div>
            </div>
        </div>
    );
}

export default DocumentSearch;
