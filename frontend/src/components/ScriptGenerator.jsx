import { useState } from 'react';

const ScriptGenerator = () => {
    const [topic, setTopic] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [script, setScript] = useState(null);
    const [audioUrl, setAudioUrl] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setScript(null);
        setAudioUrl('');

        try {
            const response = await fetch('http://localhost:5000/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to generate script');
            }

            setScript(data.script);
            setAudioUrl(`http://localhost:5000/api/audio/${data.audioFile}`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mx-auto p-4 max-w-4xl">
            <div className="bg-white rounded-lg shadow p-6">
                <h1 className="text-2xl font-bold mb-6">KJ Gemini-TTS App</h1>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        placeholder="Enter your video topic"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        disabled={loading}
                        className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                    />

                    <button
                        type="submit"
                        disabled={loading || !topic.trim()}
                        className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                        {loading ? 'Generating...' : 'Generate Script'}
                    </button>
                </form>

                {error && (
                    <div className="mt-4 p-4 bg-red-50 text-red-600 rounded">
                        {error}
                    </div>
                )}

                {script && (
                    <div className="mt-6 space-y-4">
                        <h2 className="text-xl font-bold">{script.title}</h2>

                        {script.sections.map((section, index) => (
                            <div key={index} className="space-y-2">
                                <h3 className="font-semibold">{section.text}</h3>
                                {section.scenes.length > 0 && (
                                    <div className="pl-4">
                                        {section.scenes.map((scene, sceneIndex) => (
                                            <p key={sceneIndex} className="text-gray-600">
                                                Scene {sceneIndex + 1}: {scene}
                                            </p>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ))}

                        {audioUrl && (
                            <div className="mt-4">
                                <h3 className="font-semibold mb-2">Generated Audio:</h3>
                                <audio controls className="w-full">
                                    <source src={audioUrl} type="audio/mpeg" />
                                    Your browser does not support the audio element.
                                </audio>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ScriptGenerator;