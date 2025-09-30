<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Meta tags cho SEO -->
    <meta name="description" content="Cung cấp tài khoản VIP Fshare với giá ưu đãi">
    <meta name="keywords" content="fshare vip, tài khoản fshare, addon kodi, vietmediaf, xem phim fshare">
    <meta name="author" content="Fshare.vip">
    <meta property="og:title" content="Fshare.vip - Đại lý ủy quyền Fshare.vn & Addon Kodi VietMediaF">
    <meta property="og:description" content="Cung cấp tài khoản VIP Fshare với giá ưu đãi và Addon Kodi VietMediaF cho trải nghiệm giải trí tuyệt vời">
    <meta property="og:image" content="img/og-image.jpg">
    <meta property="og:url" content="https://fshare.vip">
    <link rel="canonical" href="https://fshare.vip">
    <title>Fshare.vip - Đại lý ủy quyền Fshare.vn & Addon Kodi VietMediaF</title>
    <style>
        :root {
            --primary-color: #e74c3c;     /* Đỏ */
            --secondary-color: #f1c40f;   /* Vàng */
            --accent-color: #3498db;      /* Xanh dương */
            --text-color: #2c3e50;        /* Xám đậm */
            --light-bg: #ecf0f1;          /* Xám nhạt */
            --dark-bg: #34495e;           /* Xám đen */
            --success-color: #2ecc71;     /* Xanh lá */
            --border-color: #e5e7eb;      /* Màu viền nhẹ nhàng */
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f5f5;
            color: var(--text-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem;
        }

        /* Navigation */
        nav {
            background-color: var(--dark-bg);
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .nav-logo {
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
            text-decoration: none;
        }

        .nav-menu {
            display: flex;
            list-style: none;
        }

        .nav-menu li {
            margin-left: 1.5rem;
        }

        .nav-menu a {
            color: white;
            text-decoration: none;
            transition: color 0.3s;
        }

        .nav-menu a:hover {
            color: var(--secondary-color);
        }

        .mobile-menu-btn {
            display: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                        url('img/hero_desktop.jpg') center/cover no-repeat;
            color: white;
            text-align: center;
            padding: 5rem 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }

        /* Media query cho mobile */
        @media screen and (max-width: 768px) {
            .hero {
                background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                            url('img/hero_mobile.jpg') center/cover no-repeat;
                padding: 3rem 1rem; /* Giảm padding trên mobile */
            }

            .hero h1 {
                font-size: 2rem; /* Giảm font size trên mobile */
            }

            .hero p {
                font-size: 1rem;
                margin: 0 auto 1.5rem;
            }
        }

        /* Thêm preload cho ảnh để tối ưu hiệu suất */
        @media screen and (min-width: 769px) {
            body::after {
                position: absolute;
                width: 0;
                height: 0;
                overflow: hidden;
                z-index: -1;
                content: url('img/hero_desktop.jpg');
            }
        }

        @media screen and (max-width: 768px) {
            body::after {
                position: absolute;
                width: 0;
                height: 0;
                overflow: hidden;
                z-index: -1;
                content: url('img/hero_mobile.jpg');
            }
        }

        .hero::before {
            content: '';
            position: absolute;
            top: -10%;
            left: -10%;
            width: 120%;
            height: 120%;
            background: linear-gradient(45deg, var(--primary-color), var(--accent-color), var(--secondary-color));
            opacity: 0.3;
            animation: bgAnimation 15s linear infinite;
            z-index: -1;
        }

        @keyframes bgAnimation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .hero h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            animation: fadeInDown 1s ease;
        }

        .hero p {
            font-size: 1.2rem;
            max-width: 800px;
            margin: 0 auto 2rem;
            animation: fadeInUp 1s ease;
        }

        .promotion-banner {
            background: var(--secondary-color);
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 8px;
            animation: pulse 2s infinite;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
            50% { transform: scale(1.02); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
            100% { transform: scale(1); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        }

        /* Price Section */
        .section-title {
            text-align: center;
            margin: 2rem 0 1rem;
            position: relative;
            font-size: 2rem;
            color: var(--dark-bg);
        }

        .section-title::after {
            content: "";
            display: block;
            width: 80px;
            height: 4px;
            background: var(--primary-color);
            margin: 15px auto 0;
            border-radius: 2px;
        }

        .section-subtitle {
            text-align: center;
            color: var(--primary-color);
            margin-bottom: 2rem;
            font-size: 1.2rem;
        }

        .price-section, .comparison-wrapper, .addon-section, .faq-section, .testimonials {
            margin: 2rem 0;
        }

        .price-section-title {
            text-align: center;
            margin-bottom: 2rem;
            color: var(--dark-bg);
            font-size: 1.8rem;
            position: relative;
            display: inline-block;
            padding-bottom: 10px;
        }

        .price-section-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--accent-color);
        }

        .price-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 1.5rem;
            justify-content: center;
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            border-top: 5px solid var(--primary-color);
            max-width: 350px;
            margin: 0 auto;
            width: 100%;
        }

        .card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }

        .popular-tag {
            position: absolute;
            top: 15px;
            right: -35px;
            background: var(--accent-color);
            color: white;
            padding: 8px 40px;
            transform: rotate(45deg);
            font-size: 0.9rem;
            font-weight: bold;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10;
        }

        .card-title {
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 1rem;
            text-align: center;
            position: relative;
            padding-bottom: 15px;
        }

        .card-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 2px;
            background: var(--accent-color);
        }

        .price {
            font-size: 1.8rem;
            color: var(--dark-bg);
            text-align: center;
            margin: 1rem 0;
            font-weight: bold;
        }

        .price-original {
            text-decoration: line-through;
            color: #999;
            font-size: 1.3rem;
            display: block;
            margin-bottom: 0.5rem;
        }

        .price-savings {
            color: var(--success-color);
            font-size: 0.9rem;
            display: block;
            margin-top: 0.5rem;
        }

        .features {
            list-style: none;
            margin: 0.8rem 0;
        }

        .features li {
            margin: 0.8rem 0;
            padding-left: 2rem;
            position: relative;
            font-size: 0.95rem;
        }

        .features li::before {
            content: "✓";
            color: var(--success-color);
            position: absolute;
            left: 0;
            font-weight: bold;
        }

        .btn {
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 1rem 1.8rem;
            border-radius: 50px;
            text-decoration: none;
            text-align: center;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
        }

        .btn:hover {
            background: #c0392b;
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(231, 76, 60, 0.4);
        }

        .btn-secondary {
            background: var(--accent-color);
            box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
        }

        .btn-secondary:hover {
            background: #2980b9;
            box-shadow: 0 6px 15px rgba(52, 152, 219, 0.4);
        }

        .btn-full {
            display: block;
            width: 100%;
        }

        /* Comparison table */
        .comparison-wrapper {
            background: var(--light-bg);
            padding: 3rem 2rem;
            border-radius: 15px;
            margin: 3rem 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            animation: fadeIn 1s ease;
        }

        .comparison-title {
            text-align: center;
            margin-bottom: 2rem;
            color: var(--dark-bg);
        }

        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin: 0 auto;
            background: white;
            max-width: 900px;
            font-size: 0.95rem;
        }

        .comparison-table th,
        .comparison-table td {
            padding: 0.8rem;
            text-align: center;
            border: 1px solid #eee;
        }

        .comparison-table th {
            background: var(--primary-color);
            color: white;
            font-size: 1.1rem;
        }

        .comparison-table tr:nth-child(even) {
            background: #f9f9f9;
        }

        .comparison-table tr:hover {
            background: #f1f1f1;
        }

        .comparison-table .highlight {
            background: #fffde7;
            font-weight: bold;
        }

        .comparison-table .savings {
            color: var(--success-color);
            font-weight: bold;
        }

        /* Addon Kodi Section */
        .addon-section {
            background: var(--light-bg);
            padding: 3rem 0;
            margin: 3rem 0;
            border-radius: 15px;
            position: relative;
            overflow: hidden;
            animation: fadeIn 1s ease;
        }

        .addon-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .addon-img {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            transition: transform 0.5s ease;
            border: 5px solid white;
            width: 100%;
            height: auto;
            max-width: 500px;
            display: block;
            margin: 0 auto;
        }

        .addon-img:hover {
            transform: scale(1.02);
        }

        /* Style cho container chứa buttons */
        .addon-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .addon-buttons .btn {
            flex: 1;
            text-align: center;
            white-space: nowrap;
        }
        
        @media (max-width: 576px) {
            .addon-buttons {
                flex-direction: column;
            }
            
            .addon-buttons .btn {
                width: 100%;
                margin: 0 !important;  /* Override inline margin */
            }
        }

        /* FAQ Section */
        .faq-section {
            margin: 4rem 0;
            animation: fadeIn 1s ease;
        }

        .faq-item {
            margin-bottom: 1.5rem;
            border: 1px solid #eee;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }

        .faq-item:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }

        .faq-question {
            background: white;
            padding: 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.3s;
        }

        .faq-question:hover {
            background: #f9f9f9;
        }

        .faq-question h3 {
            font-size: 1.1rem;
            color: var(--dark-bg);
        }

        .faq-answer {
            padding: 0 1.5rem;
            max-height: 0;
            overflow: hidden;
            transition: all 0.5s ease;
            background: #f9f9f9;
        }

        .faq-item.active .faq-answer {
            padding: 1.5rem;
            max-height: 500px;
        }

        .faq-toggle {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: var(--light-bg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .faq-item.active .faq-toggle {
            background: var(--primary-color);
            color: white;
            transform: rotate(45deg);
        }

        /* Testimonials */
        .testimonials {
            margin: 3rem 0;
            position: relative;
            animation: fadeIn 1s ease;
        }

        .testimonial-container {
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            gap: 2rem;
            padding: 2rem 0;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }

        .testimonial-container::-webkit-scrollbar {
            display: none;
        }

        .testimonial-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            min-width: 300px;
            margin: 0 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }

        .testimonial-card:hover {
            transform: translateY(-5px);
        }

        .testimonial-avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            margin-bottom: 1rem;
            object-fit: cover;
            border: 3px solid var(--primary-color);
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }

        .testimonial-content {
            font-style: italic;
            margin-bottom: 1.5rem;
            color: var(--text-color);
        }

        .testimonial-author {
            font-weight: bold;
            color: var(--dark-bg);
        }

        .testimonial-role {
            color: var(--primary-color);
            font-size: 0.9rem;
        }

        .testimonial-nav {
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 1.5rem;
        }

        .testimonial-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ddd;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .testimonial-dot.active {
            background: var(--primary-color);
            transform: scale(1.2);
        }

        /* Quick Registration */
        .quick-reg {
            background: var(--light-bg);
            padding: 3rem 0;
            margin: 3rem 0;
        }

        .contact-buttons {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }

        .contact-button {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            color: white;
            font-weight: 500;
            transition: all 0.3s ease;
            min-width: 200px;
        }

        .contact-button img {
            width: 24px;
            height: 24px;
        }

        .contact-button.zalo {
            background: #0068ff;
        }

        .contact-button.messenger {
            background: #0084ff;
        }

        .contact-button.telegram {
            background: #0088cc;
        }

        .contact-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            .contact-buttons {
                flex-direction: column;
                align-items: center;
                gap: 1rem;
            }

            .contact-button {
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }
        }

        /* Footer */
        footer {
            background: var(--dark-bg);
            color: white;
            padding: 4rem 0 2rem;
            margin-top: 4rem;
            position: relative;
        }

        footer::before {
            content: '';
            position: absolute;
            top: -30px;
            left: 0;
            width: 100%;
            height: 30px;
            background: var(--dark-bg);
            clip-path: polygon(0 0, 50% 100%, 100% 0);
        }

        .footer-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 3rem;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }

        .footer-col h3 {
            position: relative;
            margin-bottom: 1.5rem;
            padding-bottom: 0.8rem;
            font-size: 1.3rem;
        }

        .footer-col h3::after {
            content: '';
            position: absolute;
            left: 0;
            bottom: 0;
            width: 50px;
            height: 3px;
            background: var(--primary-color);
        }

        .footer-links {
            list-style: none;
        }

        .footer-links li {
            margin-bottom: 1rem;
        }

        .footer-links a {
            color: #bdc3c7;
            text-decoration: none;
            transition: all 0.3s ease;
            display: inline-block;
        }

        .footer-links a:hover {
            color: white;
            transform: translateX(5px);
        }

        .social-links {
            display: flex;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .social-links a {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            color: white;
            text-decoration: none;
            transition: all 0.3s ease;
        }

        .social-links a:hover {
            background: var(--primary-color);
            transform: translateY(-3px);
        }

        .copyright {
            text-align: center;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255,255,255,0.1);
            color: #bdc3c7;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in {
            animation: fadeIn 1s ease forwards;
        }

        .fade-in-up {
            animation: fadeInUp 1s ease forwards;
        }

        .fade-in-down {
            animation: fadeInDown 1s ease forwards;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            .nav-container {
                padding: 0.5rem 1rem;
            }

            .nav-menu {
                position: fixed;
                top: 60px;
                right: -100%;
                flex-direction: column;
                background: var(--dark-bg);
                width: 80%;
                height: calc(100vh - 60px);
                padding: 2rem;
                transition: right 0.3s;
                z-index: 1000;
            }

            .nav-menu.active {
                right: 0;
            }

            .nav-menu li {
                margin: 1.5rem 0;
            }

            .mobile-menu-btn {
                display: block;
            }

            .addon-container {
                grid-template-columns: 1fr;
                gap: 2rem;
            }

            .hero h1 {
                font-size: 2rem;
            }

            .comparison-table {
                font-size: 0.9rem;
            }

            .comparison-table th,
            .comparison-table td {
                padding: 0.8rem 0.5rem;
            }

            .section-title {
                margin: 2rem 0 1rem;
                font-size: 1.75rem;
            }
            
            .price-cards {
                gap: 1rem;
            }
            
            .hero {
                padding: 2.5rem 1rem;
            }
            
            .special-promotion {
                margin: 2rem 0;
                padding: 2rem 1rem;
            }
            
            .addon-section {
                padding: 2rem 0;
                margin: 2rem 0;
            }
        }

        /* Điều chỉnh cho màn hình rất nhỏ */
        @media (max-width: 480px) {
            .hero h1 {
                font-size: 1.75rem;
            }
            
            .hero p {
                font-size: 1rem;
            }
            
            .section-title {
                font-size: 1.5rem;
            }
            
            .card {
                padding: 1.25rem;
            }
            
            .price {
                font-size: 1.75rem;
            }
            
            .features li {
                margin: 0.75rem 0;
            }
        }

        /* Thêm style cho nút so sánh */
        .comparison-action {
            text-align: center;
            margin-top: 2rem;
        }

        /* Style cho phần liên hệ */
        .contact-buttons {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin: 2rem 0;
        }

        .contact-button {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-decoration: none;
            color: white;
            font-weight: bold;
            transition: all 0.3s ease;
            min-width: 200px;
        }

        .contact-button img {
            width: 32px;
            height: 32px;
            border-radius: 50%;
        }

        .contact-button.zalo {
            background: #0068ff;
        }

        .contact-button.messenger {
            background: #0084ff;
        }

        .contact-button.telegram {
            background: #0088cc;
        }

        .contact-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        @media (max-width: 768px) {
            .contact-buttons {
                flex-direction: column;
                align-items: center;
                gap: 1rem;
            }
            
            .contact-button {
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }
        }

        /* Responsive cho addon section */
        @media (max-width: 992px) {
            .addon-container {
                grid-template-columns: 1fr;
                gap: 2rem;
            }
            
            .addon-img {
                max-width: 400px;
                margin: 2rem auto;
            }
        }

        @media (max-width: 576px) {
            .addon-container {
                padding: 0 1rem;
            }
            
            .addon-img {
                max-width: 100%;
            }
        }

        /* Thêm style cho section About */
        .about-section {
            padding: 4rem 0;
            background-color: var(--light-bg);
        }

        .about-content {
            max-width: 900px;
            margin: 0 auto;
            text-align: center;
        }

        .about-text {
            font-size: 1.2rem;
            line-height: 1.8;
            color: var(--text-color);
            margin-bottom: 3rem;
        }

        .about-stats {
            display: flex;
            justify-content: center;
            gap: 4rem;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .stat-label {
            font-size: 1.1rem;
            color: var(--text-color);
        }

        /* Responsive */
        @media screen and (max-width: 768px) {
            .about-text {
                font-size: 1.1rem;
                padding: 0 1rem;
            }
            
            .about-stats {
                gap: 2rem;
            }
            
            .stat-number {
                font-size: 2rem;
            }
            
            .stat-label {
                font-size: 1rem;
            }
        }

        /* Style cho popup */
        .popup-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 9999;
            animation: fadeIn 0.3s ease;
        }

        .popup-container {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 15px;
            max-width: 400px;
            width: 90%;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: slideIn 0.3s ease;
        }

        .popup-close {
            position: absolute;
            top: 15px;
            right: 15px;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-color);
            transition: color 0.3s;
        }

        .popup-close:hover {
            color: var(--primary-color);
        }

        .popup-title {
            font-size: 1.5rem;
            color: var(--primary-color);
            margin-bottom: 1rem;
        }

        .popup-form {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1.5rem;
        }

        .popup-input {
            padding: 0.8rem 1rem;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }

        .popup-input:focus {
            border-color: var(--primary-color);
            outline: none;
        }

        .popup-submit {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 1rem;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }

        .popup-submit:hover {
            background: var(--primary-dark);
        }

        @keyframes slideIn {
            from {
                transform: translate(-50%, -60%);
                opacity: 0;
            }
            to {
                transform: translate(-50%, -50%);
                opacity: 1;
            }
        }

        /* Thêm Quick Jump Menu */
        .quick-jump {
            background: white;
            padding: 1rem 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 70px;
            z-index: 100;
            margin-bottom: 2rem;
        }

        .quick-jump-menu {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            list-style: none;
            margin: 0;
            padding: 0;
        }

        .quick-jump-menu a {
            color: var(--text-color);
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            transition: all 0.3s;
        }

        .quick-jump-menu a:hover,
        .quick-jump-menu a.active {
            background: var(--primary-color);
            color: white;
        }

        /* Floating CTA Button */
        .floating-cta {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
            animation: bounce 2s infinite;
        }

        .cta-button {
            background: var(--primary-color);
            color: white;
            padding: 1rem 2rem;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .quick-jump {
                overflow-x: auto;
                padding: 0.5rem;
            }
            
            .quick-jump-menu {
                width: max-content;
                padding: 0 1rem;
            }
            
            .floating-cta {
                bottom: 1rem;
                right: 1rem;
            }
        }

        /* Điều chỉnh grid cho màn hình lớn */
        @media (min-width: 992px) {
            .price-cards {
                grid-template-columns: repeat(2, 350px);
            }
        }

        /* Điều chỉnh cho màn hình nhỏ */
        @media (max-width: 991px) {
            .price-cards {
                grid-template-columns: minmax(auto, 350px);
                max-width: 400px;
            }
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav>
        <div class="nav-container">
            <a href="#" class="nav-logo">FSHARE.VIP</a>
            <ul class="nav-menu">
                <li><a href="#">Trang chủ</a></li>
                <li><a href="#personal-account">Tài khoản Cá nhân</a></li>
                <li><a href="#group-account">Tài khoản Ghép nhóm</a></li>
                <li><a href="#addon">Addon Kodi</a></li>
                <li><a href="#faq">Hỏi đáp</a></li>
                <li><a href="#contact">Liên hệ</a></li>
            </ul>
            <div class="mobile-menu-btn">☰</div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Giải pháp hoàn chỉnh cho trải nghiệm Fshare</h1>
            <p>Tài khoản VIP chính hãng với giá ưu đãi 
            <br>
            Addon Kodi VietMediaF - Xem phim, nghe nhạc không giới hạn</p>
            <a href="#personal-account" class="btn">Xem gói dịch vụ</a>
            
            <div class="promotion-banner">
                <div class="promotion-content">
                    <h3>🎉 KHUYẾN MÃI MỪNG NGÀY 30/04 🎉</h3>
                    <p>Từ 04/04 - 01/05: GIẢM 20% GIÁ VÀ TẶNG 20% NGÀY CHO CÁC GÓI</p>
                    <p>03 tháng tặng 18 ngày | 12 tháng tặng 108 ngày</p>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section class="about-section">
        <div class="container">
            <div class="about-content">
                <p class="about-text">
                    Với hơn 8 năm kinh nghiệm, chúng tôi tự hào là đối tác uy tín của Fshare.vn (FPT Telecom), 
                    mang đến cho khách hàng không chỉ giá cả ưu đãi mà còn kèm theo các tiện ích Kodi khai thác 
                    tài nguyên trên Fshare như Addon VietMediaF, Fshare...
                </p>
                
                <div class="about-stats">
                    <div class="stat-item">
                        <div class="stat-number">8+</div>
                        <div class="stat-label">Năm kinh nghiệm</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">20K+</div>
                        <div class="stat-label">Khách hàng tin dùng</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Personal Account Section -->
    <section id="personal-account" class="price-section container">
        <h2 class="section-title">Tài khoản Fshare Cá nhân</h2>
        <div class="price-cards">
            <div class="card">
                <h3 class="card-title">Gói 1 tháng</h3>
                <div class="price">
                    <span class="price-original">90.000đ</span>
                    81.000đ
                    <span class="price-savings">Tiết kiệm 9.000đ</span>
                </div>
                <ul class="features">
                    <li>Thời hạn 1 tháng</li>
                    <li>Tốc độ tải không giới hạn</li>
                    <li>Dung lượng lưu trữ 300Gb</li>
                    <li>Lưu lượng tốc độ cao 200Gb</li>
                    <li>Tải nhiều file cùng lúc</li>
                    <li>Không giới hạn dung lượng file</li>
                    <li>Tải trên 3 thiết bị</li>
                </ul>
                <a href="#quick-reg" class="btn btn-full">Đăng ký ngay</a>
            </div>

            <div class="card">
                <div class="popular-tag">Phổ biến</div>
                <h3 class="card-title">Gói 3 tháng</h3>
                <div class="price">
                    <span class="price-original">230.000đ</span>
                    170.000đ
                    <span class="price-savings">Tiết kiệm 60.000đ</span>
                </div>
                <ul class="features">
                    <li>Thời hạn 3 tháng + 18 ngày</li>
                    <li>Tốc độ tải không giới hạn</li>
                    <li>Dung lượng lưu trữ 300GB</li>
                    <li>Lưu lượng tốc độ cao 200Gb</li>
                    <li>Tải nhiều file cùng lúc</li>
                    <li>Không giới hạn dung lượng file</li>
                    <li>Tải trên 3 thiết bị</li>
                </ul>
                <a href="#quick-reg" class="btn btn-full">Đăng ký ngay</a>
            </div>

            <div class="card">
                <div class="popular-tag">Phổ biến</div>
                <h3 class="card-title">Gói 12 tháng</h3>
                <div class="price">
                    <span class="price-original">690.000đ</span>
                    525.000đ
                    <span class="price-savings">Tiết kiệm 165.000đ</span>
                </div>
                <ul class="features">
                    <li>Thời hạn 12 tháng + 108 ngày</li>
                    <li>Tốc độ tải không giới hạn</li>
                    <li>Dung lượng lưu trữ 300Gb</li>
                    <li>Lưu lượng tốc độ cao 300Gb</li>
                    <li>Tải nhiều file cùng lúc</li>
                    <li>Không giới hạn dung lượng file</li>
                    <li>Tải trên 3 thiết bị</li>
                </ul>
                <a href="#quick-reg" class="btn btn-full">Đăng ký ngay</a>
            </div>

            <div class="card">
                <h3 class="card-title">Gói 24 tháng</h3>
                <div class="price">
                    <span class="price-original">1.380.000đ</span>
                    1.050.000đ
                    <span class="price-savings">Tiết kiệm 130.000đ</span>
                </div>
                <ul class="features">
                    <li>Thời hạn 24 tháng + 216 ngày</li>
                    <li>Tốc độ tải không giới hạn</li>
                    <li>Dung lượng lưu trữ 300GB</li>
                    <li>Lưu lượng tốc độ cao 300Gb</li>
                    <li>Tải nhiều file cùng lúc</li>
                    <li>Không giới hạn dung lượng file</li>
                    <li>Tải trên 3 thiết bị</li>
                </ul>
                <a href="#quick-reg" class="btn btn-full">Đăng ký ngay</a>
            </div>
        </div>
    </section>

    <!-- Group Account Section -->
    <section id="group-account" class="price-section container">
        <h2 class="section-title">Tài khoản Fshare Ghép nhóm</h2>
        <p class="section-subtitle">Giải pháp tiết kiệm cho nhu cầu xem online</p>

        <div class="price-cards">
            <div class="card">
                <h2 class="card-title">Gói 3 tháng</h2>
                <div class="price">
                    <span class="price-original">-</span>
                    70.000đ
                    <!-- <span class="price-savings">+ 18 ngày sử dụng</span>-->
                </div>
                <ul class="features">
                    <li>Thời hạn 3 tháng + 32 ngày</li>
                    <li>Dùng trên 1 thiết bị</li>
                    <li>Chỉ dành cho xem online</li>
                    <li>Chia sẻ tài nguyên nhóm</li>
                    <li>Phù hợp xem phim, nghe nhạc</li>
                </ul>
                <a href="#quick-reg" class="btn btn-full">Đăng ký ngay</a>
            </div>
            
            <div class="card">
                <div class="popular-tag">Tiết kiệm</div>
                <h2 class="card-title">Gói 12 tháng</h2>
                <div class="price">
                    <span class="price-original">-</span>
                    220.000đ
                    <!-- <span class="price-savings">+ 73 ngày sử dụng</span>-->
                </div>
                <ul class="features">
                    <li>Thời hạn 12 tháng + 152 ngày</li>
                    <li>Dùng trên 1 thiết bị</li>
                    <li>Chỉ dành cho xem online</li>
                    <li>Chia sẻ tài nguyên nhóm</li>
                    <li>Phù hợp xem phim, nghe nhạc</li>
                    
                </ul>
                <a href="#quick-reg" class="btn btn-full">Đăng ký ngay</a>
            </div>
        </div>
    </section>

    <!-- Addon Kodi Section -->
    <section id="addon" class="addon-section">
        <div class="container">
            <h2 class="section-title">Addon Kodi VietMediaF</h2>
            <div class="addon-container">
                <div>
                    <h3>Xem phim, nghe nhạc không giới hạn từ Fshare</h3>
                    <p>Addon Kodi VietMediaF cho phép bạn dễ dàng xem phim, nghe nhạc từ Fshare trực tiếp trên TV Box, máy tính, điện thoại thông qua ứng dụng Kodi mà không cần tải về.</p>
                    <ul class="features">
                        <li>Tự động đăng nhập tài khoản Fshare</li>
                        <li>Giao diện thân thiện, dễ sử dụng</li>
                        <li>Xem phim HD, 4K không giật lag</li>
                        <li>Hỗ trợ nhiều nền tảng: Android TV, Windows, MacOS, iOS</li>
                        <li>Cập nhật thường xuyên, hỗ trợ kỹ thuật nhanh chóng</li>
                    </ul>
                    <div class="addon-buttons">
                        <a href="https://kodi.vn" class="btn btn-secondary" target="_blank">Tìm hiểu tại Kodi.vn</a>
                        <a href="https://www.facebook.com/groups/kodiviet" class="btn" target="_blank">Tham gia nhóm Facebook</a>
                    </div>
                </div>
                <div>
                    <img src="img/addonvmf.webp" alt="Addon Kodi VietMediaF" class="addon-img" loading="lazy">
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section id="faq" class="faq-section container">
        <h2 class="section-title">Câu hỏi thường gặp</h2>
        <div class="faq-item">
            <div class="faq-question">
                <h3>Tài khoản ghép nhóm có hạn chế gì so với tài khoản cá nhân?</h3>
                <div class="faq-toggle">+</div>
            </div>
            <div class="faq-answer">
                <p>Tài khoản ghép nhóm chỉ được sử dụng trên 1 thiết bị, 1 IP tại một thời điểm. Tài khoản này phù hợp cho việc xem online, không phù hợp để tải file với tốc độ cao. Dung lượng lưu trữ được chia sẻ trong nhóm.</p>
            </div>
        </div>
        <div class="faq-item">
            <div class="faq-question">
                <h3>Addon Kodi VietMediaF là gì và cách sử dụng?</h3>
                <div class="faq-toggle">+</div>
            </div>
            <div class="faq-answer">
                <p>Addon Kodi VietMediaF là tiện ích mở rộng cho phần mềm Kodi, giúp bạn xem phim, nghe nhạc trực tiếp từ Fshare mà không cần tải về. Bạn chỉ cần cài đặt Kodi, thêm Addon VietMediaF, nhập tài khoản Fshare và bắt đầu xem. Hướng dẫn chi tiết có tại website <a href="https://kodi.vn" target="_blank">kodi.vn</a>.</p>
            </div>
        </div>
        <div class="faq-item">
            <div class="faq-question">
                <h3>Tôi có thể xem Fshare trên TV thông thường không?</h3>
                <div class="faq-toggle">+</div>
            </div>
            <div class="faq-answer">
                <p>Có thể, bạn cần có một TV Box chạy Android (hoặc Android TV) hoặc thiết bị như Fire TV Stick. Sau đó cài đặt Kodi và addon VietMediaF, nhập tài khoản Fshare là có thể xem được. Chúng tôi sẽ hỗ trợ bạn cài đặt và sử dụng.</p>
            </div>
        </div>
        <div class="faq-item">
            <div class="faq-question">
                <h3>Làm thế nào để thanh toán và kích hoạt tài khoản?</h3>
                <div class="faq-toggle">+</div>
            </div>
            <div class="faq-answer">
                <p>Bạn có thể thanh toán qua chuyển khoản ngân hàng hoặc ví điện tử theo thông tin bên dưới. Sau khi thanh toán, vui lòng liên hệ với chúng tôi qua Zalo/Facebook để được kích hoạt tài khoản trong vòng 5-10 phút.</p>
            </div>
        </div>
    </section>

    <!-- Testimonials -->
    <section class="testimonials container">
        <h2 class="section-title">Đánh giá từ khách hàng</h2>
        <div class="testimonial-container">
            <div class="testimonial-card">
                <img src="img/user1.jpg" alt="Avatar" class="testimonial-avatar" width="100" height="100">
                <div class="testimonial-content">
                    <p class="testimonial-text">
                        "Dịch vụ rất tốt, tốc độ tải nhanh và ổn định. Đặc biệt là addon Kodi rất tiện lợi cho việc xem phim trên TV. Giá cả hợp lý, hỗ trợ nhiệt tình."
                    </p>
                    <div class="testimonial-author">Nguyễn Hải Anh</div>
                    <div class="testimonial-rating">⭐⭐⭐⭐⭐</div>
                </div>
            </div>
            
            <div class="testimonial-card">
                <img src="img/user2.jpg" alt="Avatar" class="testimonial-avatar" width="100" height="100">
                <div class="testimonial-content">
                    <p class="testimonial-text">
                        "Đã sử dụng dịch vụ được hơn 2 năm. Rất hài lòng với chất lượng phục vụ. Tài khoản hoạt động ổn định, không bị gián đoạn."
                    </p>
                    <div class="testimonial-author">Trần Lan Phương</div>
                    <div class="testimonial-rating">⭐⭐⭐⭐⭐</div>
                </div>
            </div>
            
            <div class="testimonial-card">
                <img src="img/user3.jpg" alt="Avatar" class="testimonial-avatar" width="100" height="100">
                <div class="testimonial-content">
                    <p class="testimonial-text">
                        "Giá rẻ hơn đăng ký trực tiếp mà còn được tặng thêm ngày sử dụng. Support rất nhanh, nhiệt tình. Sẽ tiếp tục ủng hộ dài dài."
                    </p>
                    <div class="testimonial-author">Chú Lê Văn Chương</div>
                    <div class="testimonial-rating">⭐⭐⭐⭐⭐</div>
                </div>
            </div>
        </div>
        <div class="testimonial-dots">
            <span class="testimonial-dot active"></span>
            <span class="testimonial-dot"></span>
            <span class="testimonial-dot"></span>
        </div>
    </section>

    <!-- Quick Registration -->
    <section id="quick-reg" class="quick-reg">
        <div class="container">
            <h2 class="section-title">Đăng ký nhanh</h2>
            <div class="contact-buttons">
                <a href="https://zalo.me/0915134560" class="contact-button zalo" target="_blank">
                    <img src="img/zalo.png" alt="Zalo">
                    <span>Chat Zalo ngay</span>
                </a>
                <a href="https://m.me/duchanoi" class="contact-button messenger" target="_blank">
                    <img src="img/mess.png" alt="Messenger">
                    <span>Nhắn tin Messenger</span>
                </a>
                <a href="https://t.me/ducnn" class="contact-button telegram" target="_blank">
                    <img src="img/telegram.png" alt="Telegram">
                    <span>Chat Telegram</span>
                </a>
            </div>
            <p style="text-align: center; margin-top: 1rem;">
                Chọn một trong các phương thức liên hệ trên để được tư vấn và đăng ký nhanh chóng
            </p>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="footer-container">
            <div class="footer-col">
                <h3>Fshare.vip</h3>
                <p>Đại lý ủy quyền chính thức của Fshare.vn - Cung cấp tài khoản VIP với giá ưu đãi cùng nhiều tiện ích độc quyền.</p>
                <div class="social-links">
                    <a href="https://www.facebook.com/vietmediaF" target="_blank">FB</a>
                    <a href="https://www.facebook.com/groups/kodiviet" target="_blank">G</a>
                    <a href="https://zalo.me/0915134560" target="_blank">ZL</a>
                </div>
            </div>
            <div class="footer-col">
                <h3>Dịch vụ</h3>
                <ul class="footer-links">
                    <li><a href="#personal-account">Tài khoản Fshare Cá nhân</a></li>
                    <li><a href="#group-account">Tài khoản Fshare Ghép nhóm</a></li>
                    <li><a href="#addon">Addon Kodi VietMediaF</a></li>
                    <li><a href="https://kodi.vn" target="_blank">Hướng dẫn cài đặt Kodi</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h3>Liên kết</h3>
                <ul class="footer-links">
                    <li><a href="https://www.facebook.com/vietmediaF" target="_blank">Fanpage Facebook</a></li>
                    <li><a href="https://www.facebook.com/groups/kodiviet" target="_blank">Group Facebook Kodiviet</a></li>
                    <li><a href="https://kodi.vn" target="_blank">Website Kodi.vn</a></li>
                    <li><a href="https://fshare.vn" target="_blank">Fshare.vn chính thức</a></li>
                </ul>
            </div>
            <div class="footer-col">
                <h3>Liên hệ</h3>
                <ul class="footer-links">
                    <li>📱 Điện thoại: 0915134560</li>
                    <li>📧 Email: vietkodi@gmail.com</li>
                    <li>🔗 Zalo: 0915134560</li>
                    <li>⏰ Hỗ trợ: 8h-22h hàng ngày</li>
                </ul>
            </div>
        </div>
        <div class="copyright">
            <p>&copy; 2024 Fshare.vip - Đại lý ủy quyền chính thức của Fshare.vn</p>
        </div>
    </footer>

    <!-- Thêm vào cuối body trước </body> -->
    <div class="popup-overlay" id="promoPopup">
        <div class="popup-container">
            <div class="popup-close" onclick="closePopup()">&times;</div>
            <h3 class="popup-title">Nhận thông tin khuyến mãi</h3>
            <p>Đăng ký để nhận ngay thông tin về các chương trình khuyến mãi mới nhất từ Fshare.vip</p>
            <form class="popup-form" id="promoForm" onsubmit="submitPromoForm(event)">
                <input type="email" class="popup-input" placeholder="Nhập email của bạn" required>
                <button type="submit" class="popup-submit">Đăng ký ngay</button>
            </form>
        </div>
    </div>

    <!-- Quick Jump Menu -->
    <div class="quick-jump">
        <div class="container">
            <ul class="quick-jump-menu">
                <li><a href="#personal-account">Tài khoản Cá nhân</a></li>
                <li><a href="#group-account">Tài khoản Ghép nhóm</a></li>
                <li><a href="#addon">Addon Kodi</a></li>
                <li><a href="#faq">Hỏi đáp</a></li>
            </ul>
        </div>
    </div>

    <!-- Floating CTA Button -->
    <div class="floating-cta">
        <a href="#quick-reg" class="cta-button">
            <i class="bi bi-chat-dots-fill"></i>
            Đăng ký ngay
        </a>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Mobile menu toggle
            const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
            const navMenu = document.querySelector('.nav-menu');
            
            if (mobileMenuBtn) {
                mobileMenuBtn.addEventListener('click', function() {
                    navMenu.classList.toggle('active');
                    mobileMenuBtn.textContent = navMenu.classList.contains('active') ? '✕' : '☰';
                });
            }

            // Smooth scrolling
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    if (targetId === '#') return;
                    
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - 70,
                            behavior: 'smooth'
                        });
                        
                        // Close mobile menu if open
                        if (navMenu.classList.contains('active')) {
                            navMenu.classList.remove('active');
                            mobileMenuBtn.textContent = '☰';
                        }
                    }
                });
            });

            // FAQ accordion
            const faqQuestions = document.querySelectorAll('.faq-question');
            
            faqQuestions.forEach(question => {
                question.addEventListener('click', () => {
                    const faqItem = question.parentElement;
                    const isActive = faqItem.classList.contains('active');
                    
                    // Close all FAQ items
                    document.querySelectorAll('.faq-item').forEach(item => {
                        item.classList.remove('active');
                        item.querySelector('.faq-toggle').textContent = '+';
                    });
                    
                    // Open clicked item if it wasn't active
                    if (!isActive) {
                        faqItem.classList.add('active');
                        question.querySelector('.faq-toggle').textContent = '−';
                    }
                });
            });

            // Testimonial slider
            const testimonialDots = document.querySelectorAll('.testimonial-dot');
            const testimonialContainer = document.querySelector('.testimonial-container');
            const testimonialCards = document.querySelectorAll('.testimonial-card');
            
            if (testimonialDots.length > 0 && testimonialContainer && testimonialCards.length > 0) {
                testimonialDots.forEach((dot, index) => {
                    dot.addEventListener('click', () => {
                        // Remove active class from all dots
                        testimonialDots.forEach(d => d.classList.remove('active'));
                        
                        // Add active class to clicked dot
                        dot.classList.add('active');
                        
                        // Calculate scroll position
                        const cardWidth = testimonialCards[0].offsetWidth + 32; // width + gap
                        testimonialContainer.scrollTo({
                            left: index * cardWidth,
                            behavior: 'smooth'
                        });
                    });
                });
            }

            // Animation on scroll
            const animateElements = document.querySelectorAll('.price-section, .comparison-wrapper, .addon-section, .faq-section, .testimonials, .quick-reg');
            
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('fade-in');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            
            animateElements.forEach(element => {
                observer.observe(element);
            });

            // Thêm vào phần script hiện có
            document.addEventListener('DOMContentLoaded', function() {
                // Quick Jump Menu active state
                const quickJumpLinks = document.querySelectorAll('.quick-jump-menu a');
                const sections = document.querySelectorAll('section[id]');
                
                window.addEventListener('scroll', () => {
                    let current = '';
                    
                    sections.forEach(section => {
                        const sectionTop = section.offsetTop;
                        if (window.pageYOffset >= sectionTop - 100) {
                            current = section.getAttribute('id');
                        }
                    });
                    
                    quickJumpLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href').slice(1) === current) {
                            link.classList.add('active');
                        }
                    });
                });
            });
        });

        // Thêm vào phần script hiện có
        function showPopup() {
            if (!localStorage.getItem('popupShown')) {
                setTimeout(() => {
                    document.getElementById('promoPopup').style.display = 'block';
                }, 5000); // Hiện popup sau 5 giây
            }
        }

        function closePopup() {
            document.getElementById('promoPopup').style.display = 'none';
            localStorage.setItem('popupShown', 'true');
        }

        async function submitPromoForm(event) {
            event.preventDefault();
            const email = event.target.querySelector('input[type="email"]').value;
            
            try {
                const response = await fetch('/api/subscribe.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email })
                });
                
                if (response.ok) {
                    alert('Cảm ơn bạn đã đăng ký! Chúng tôi sẽ gửi thông tin khuyến mãi sớm nhất.');
                    closePopup();
                } else {
                    throw new Error('Có lỗi xảy ra');
                }
            } catch (error) {
                alert('Có lỗi xảy ra, vui lòng thử lại sau!');
            }
        }

        // Thêm vào DOMContentLoaded
        document.addEventListener('DOMContentLoaded', function() {
            // ... existing code ...
            showPopup();
        });
    </script>
</body>
</html>