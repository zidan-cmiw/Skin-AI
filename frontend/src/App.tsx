import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import './index.css';

const Layout = ({ children }: { children: React.ReactNode }) => {
    const location = useLocation();
    
    return (
        <div className="dashboard-container">
            <aside className="sidebar">
                <div className="logo">
                    <i className="fa-solid fa-face-smile"></i>
                    <div>
                        <h2>SkinAI</h2>
                        <p>AI Skin Analysis</p>
                    </div>
                </div>
                <nav className="nav-menu">
                    <Link to="/" className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
                        <i className="fa-solid fa-house"></i> Dashboard
                    </Link>
                    <Link to="/analyze" className={`nav-item ${location.pathname === '/analyze' ? 'active' : ''}`}>
                        <i className="fa-solid fa-expand"></i> AI Skin Analysis
                    </Link>
                    <a href="#" className="nav-item">
                        <i className="fa-solid fa-clock-rotate-left"></i> History
                    </a>
                    <a href="#" className="nav-item">
                        <i className="fa-regular fa-lightbulb"></i> Tips
                    </a>
                </nav>

                <div className="sidebar-profile">
                    <div className="profile-icon">
                        <i className="fa-solid fa-user"></i>
                    </div>
                    <div className="profile-info">
                        <strong>Putri Aulia</strong>
                        <span>View Profile</span>
                    </div>
                    <i className="fa-solid fa-chevron-right chevron"></i>
                </div>
            </aside>
            <main className="main-content">
                <header className="header">
                    <div>
                        <h1>{location.pathname === '/' ? 'Dashboard' : 'AI Skin Analysis'}</h1>
                        <p>{location.pathname === '/' ? 'Halo, Putri! Yuk, jaga kesehatan kulitmu ✨' : 'Unggah foto wajah Anda untuk analisis kulit'}</p>
                    </div>
                    <div className="header-right">
                         <div className="notification-icon">
                             <i className="fa-regular fa-bell"></i>
                         </div>
                    </div>
                </header>
                {children}
            </main>
        </div>
    );
};

const Dashboard = () => {
    return (
        <div className="dashboard-content">
            <div className="dashboard-grid top-grid">
                <div className="card-panel primary-card analyze-card-bg">
                    <div className="card-header">
                        <h3 style={{color: '#333'}}>Analisis Terakhir</h3>
                        <span className="date">{new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                    </div>
                    <div className="card-body type-analysis">
                        <div className="type-indicator">
                            <div className="type-icon" style={{color: '#8b5cf6'}}>💧</div>
                            <div style={{textAlign: 'left'}}>
                                <p className="type-label">Jenis Kulit</p>
                                <h2 className="type-value">Kering</h2>
                            </div>
                        </div>
                        <p className="type-desc" style={{textAlign: 'left', marginTop: '10px'}}>Kulitmu cenderung kering, perlu hidrasi lebih.</p>
                        <Link to="/analyze" className="btn-detail">Lihat Detail</Link>
                        <div className="face-illustration default-illustration">
                            <img src="https://cdn-icons-png.flaticon.com/512/4140/4140047.png" className="analyzed-face" alt="Profile" />
                        </div>
                    </div>
                </div>

                <div className="card-panel score-card">
                    <h3>Skin Score</h3>
                    <div className="score-ring">
                        <div className="score-value">
                            <h1>72</h1>
                            <span>/100</span>
                        </div>
                        <svg className="progress-ring" width="120" height="120">
                            <circle className="progress-ring__circle" stroke="#8b5cf6" strokeWidth="8" fill="transparent" r="52" cx="60" cy="60"/>
                        </svg>
                    </div>
                    <p>Kulitmu dalam kondisi cukup baik.</p>
                </div>

                <div className="card-panel recommendations-card">
                    <h3>Rekomendasi Singkat</h3>
                    <div className="recommendation-dashboard">
                         <div className="rec-dashboard-item">
                            <div className="rec-icon" style={{color: '#3b82f6', backgroundColor: '#eff6ff'}}>💧</div>
                            <div className="rec-text" style={{textAlign: 'left'}}>
                                <strong className="rec-category" style={{textTransform: 'none'}}>Perbanyak hidrasi</strong>
                                <p>Minum air 2L setiap hari</p>
                            </div>
                        </div>
                        <div className="rec-dashboard-item">
                            <div className="rec-icon" style={{color: '#22c55e', backgroundColor: '#f0fdf4'}}>🧴</div>
                            <div className="rec-text" style={{textAlign: 'left'}}>
                                <strong className="rec-category" style={{textTransform: 'none'}}>Gunakan moisturizer</strong>
                                <p>Pilih yang melembapkan</p>
                            </div>
                        </div>
                        <div className="rec-dashboard-item">
                            <div className="rec-icon" style={{color: '#eab308', backgroundColor: '#fefce8'}}>☀️</div>
                            <div className="rec-text" style={{textAlign: 'left'}}>
                                <strong className="rec-category" style={{textTransform: 'none'}}>Jangan lupa sunscreen</strong>
                                <p>Gunakan setiap pagi</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="dashboard-grid bottom-grid">
                <div className="card-panel features-card" style={{textAlign: 'left'}}>
                    <h3 style={{marginBottom: '20px'}}>Fitur Utama</h3>
                    <div className="features-grid">
                         <Link to="/analyze" className="feature-item-box">
                             <div className="feature-icon" style={{color: '#8b5cf6', backgroundColor: '#f5f3ff'}}><i className="fa-solid fa-expand"></i></div>
                             <div className="feature-text">
                                 <strong>AI Skin Analysis</strong>
                                 <p>Analisis kondisi kulitmu menggunakan AI</p>
                             </div>
                         </Link>
                         <a href="#" className="feature-item-box">
                             <div className="feature-icon" style={{color: '#8b5cf6', backgroundColor: '#f5f3ff'}}><i className="fa-solid fa-clock-rotate-left"></i></div>
                             <div className="feature-text">
                                 <strong>History</strong>
                                 <p>Lihat riwayat hasil analisis kulitmu</p>
                             </div>
                         </a>
                         <a href="#" className="feature-item-box">
                             <div className="feature-icon" style={{color: '#f43f5e', backgroundColor: '#fff1f2'}}><i className="fa-regular fa-lightbulb"></i></div>
                             <div className="feature-text">
                                 <strong>Tips</strong>
                                 <p>Dapatkan tips perawatan kulit harian</p>
                             </div>
                         </a>
                         <a href="#" className="feature-item-box">
                             <div className="feature-icon" style={{color: '#10b981', backgroundColor: '#ecfdf5'}}><i className="fa-solid fa-bottle-droplet"></i></div>
                             <div className="feature-text">
                                 <strong>Profile</strong>
                                 <p>Kelola data dan preferensi akunmu</p>
                             </div>
                         </a>
                    </div>
                </div>

                <div className="card-panel tips-card" style={{backgroundColor: '#fffbeb'}}>
                    <h3 style={{textAlign: 'left'}}>Tips Hari Ini</h3>
                    <div className="tips-content">
                        <div className="tips-icon" style={{color: '#eab308', fontSize: '32px', marginBottom: '15px'}}>☀️</div>
                        <strong style={{color: '#333'}}>Gunakan sunscreen setiap pagi</strong>
                        <p style={{color: '#555', marginTop: '5px'}}>untuk melindungi kulit dari sinar UV.</p>
                    </div>
                    <div className="tips-dots">
                        <span className="dot active"></span>
                        <span className="dot"></span>
                        <span className="dot"></span>
                    </div>
                </div>
            </div>
            <div className="footer-copyright">
                © 2024 SkinAI. All rights reserved.
            </div>
        </div>
    );
};

const Analyze = () => {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [resultData, setResultData] = useState<{
        result: string;
        recommendation: Record<string, string> | string;
        image_url: string;
        source: string;
    } | null>(null);

    const backendUrl = "http://127.0.0.1:5000";

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResultData(null);
        }
    };

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) return;
        setLoading(true);

        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await axios.post(`${backendUrl}/api/analyze`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setResultData(response.data);
        } catch (error) {
            console.error("Error analyzing skin:", error);
            alert("Error during analyzing skin. Check server.");
        } finally {
            setLoading(false);
        }
    };

    const renderRecommendations = (recommendation: Record<string, string> | string) => {
        if (typeof recommendation === 'string') {
            return <p style={{color: '#555'}}>{recommendation}</p>;
        }

        return (
            <div className="recommendation-dashboard">
                {Object.entries(recommendation).map(([category, rec], idx) => (    
                    <div key={idx} className="rec-dashboard-item">
                        <div className="rec-icon">
                            {category.toLowerCase().includes('hidrasi') || category.toLowerCase().includes('air') || category.toLowerCase().includes('toner') || category.toLowerCase().includes('cleanser') || category.toLowerCase().includes('pembersih') ? '💧' : 
                             category.toLowerCase().includes('moisturizer') || category.toLowerCase().includes('pelembap') || category.toLowerCase().includes('krim') || category.toLowerCase().includes('cream') ? '🧴' : 
                             category.toLowerCase().includes('sunscreen') || category.toLowerCase().includes('tabir surya') || category.toLowerCase().includes('uv') ? '☀️' : 
                             category.toLowerCase().includes('serum') || category.toLowerCase().includes('ampoule') || category.toLowerCase().includes('essence') ? '✨' : 
                             '🌿'}
                        </div>
                        <div className="rec-text" style={{textAlign: 'left'}}>
                            <strong className="rec-category">{category.charAt(0).toUpperCase() + category.slice(1)}</strong>
                            <p>{rec}</p>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    if (resultData) {
        return (
            <div className="dashboard-grid top-grid single-result">
                <div className="card-panel primary-card">
                    <div className="card-header">
                        <h3>Analisis Terakhir</h3>
                        <span className="date">{new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                    </div>
                    <div className="card-body type-analysis">
                        <div className="type-indicator">
                            <div className="type-icon">💧</div>
                            <div style={{textAlign: 'left'}}>
                                <p className="type-label">Jenis Kulit</p>
                                <h2 className="type-value">{resultData.result}</h2>
                            </div>
                        </div>
                        <div className="face-illustration">
                                <img src={resultData.image_url.startsWith('http') ? resultData.image_url : `${backendUrl}${resultData.image_url}`} 
                                className="analyzed-face" alt="Uploaded Profile"  
                                onError={(e) => { e.currentTarget.style.display = 'none'; }} />
                        </div>
                        <p className="type-desc" style={{textAlign: 'left', marginTop: '10px'}}>Diidentifikasi dengan {resultData.source || 'AI'}. Perlu hidrasi dan perlindungan rutin.</p>
                        
                        <button className="btn-detail" onClick={() => { setResultData(null); setFile(null); setPreview(null); }} style={{marginTop: '20px', display: 'inline-block', width: 'auto'}}>
                            Analisis Ulang
                        </button>
                    </div>
                </div>

                <div className="card-panel recommendations-card" style={{gridColumn: 'span 2'}}>
                    <h3>Rekomendasi Produk</h3>
                    {renderRecommendations(resultData.recommendation)}
                </div>
            </div>
        );
    }

    return (
        <div className="upload-container">
            <div className="card upload-card-new">
                <div className="icon" style={{color: '#8b5cf6'}}>
                    <i className="fa-solid fa-spa"></i>
                </div>
                <h1 style={{color: '#333'}}>Analisis AI</h1>
                <p className="subtitle" style={{color: '#777'}}>
                    Unggah foto wajah Anda untuk analisis kulit
                </p>
                <form onSubmit={handleAnalyze}>
                    <label className="upload-box-new">
                        <input
                            type="file"
                            name="image"
                            id="imageInput"
                            hidden
                            required
                            onChange={handleFileChange}
                        />
                        <i className="fa-solid fa-cloud-arrow-up" style={{color: '#8b5cf6', fontSize: '30px', marginBottom: '10px'}}></i>
                        <p id="uploadText" style={{color: '#777'}}>
                            {file ? file.name : "Klik untuk Mengunggah Foto Wajah"}
                        </p>
                    </label>
                    {preview && !resultData && (
                        <img id="previewImage" src={preview} alt="Preview" style={{ display: 'block', margin: '0 auto 20px', borderRadius: '10px', width: '200px', height: '200px', objectFit: 'cover' }} />
                    )}
                    <button type="submit" disabled={!file || loading} className="upload-btn">
                        <i className="fa-solid fa-wand-magic-sparkles"></i>        
                        {loading ? " Menganalisis..." : " Analisis Kulit"}
                    </button>
                </form>
            </div>
        </div>
    );
};

const App = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout><Dashboard /></Layout>} />
                <Route path="/analyze" element={<Layout><Analyze /></Layout>} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
