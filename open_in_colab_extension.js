// ==UserScript==
// @name         GitHub "Open in Google Colab" Extension
// @namespace    https://github.com/overandor
// @version      1.0
// @description  Adds a direct "Open in Google Colab" button to any Jupyter Notebook (.ipynb) on GitHub
// @author       Antigravity
// @match        https://github.com/*/*.ipynb
// @match        https://github.com/*
// @grant        none
// ==UserScript==

(function() {
    'use strict';

    function addColabButton() {
        const path = window.location.pathname;
        if (!path.endsWith('.ipynb')) return;
        if (document.getElementById('open-in-colab-btn')) return;

        // Convert GitHub URL to Google Colab URL
        // Example: /overandor/CodeRunnerApp/blob/main/hdar_canonical_proof.ipynb
        const colabUrl = `https://colab.research.google.com/github${path}`;

        // Find GitHub file header button bar
        const actionHeader = document.querySelector('.file-actions') || 
                             document.querySelector('[data-aria-label="File actions"]') ||
                             document.querySelector('.Box-header');

        if (actionHeader) {
            const btn = document.createElement('a');
            btn.id = 'open-in-colab-btn';
            btn.href = colabUrl;
            btn.target = '_blank';
            btn.style.cssText = `
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background-color: #f9ab00;
                color: #000;
                font-weight: 700;
                font-size: 12px;
                padding: 4px 12px;
                border-radius: 6px;
                text-decoration: none;
                margin-left: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            `;
            btn.innerHTML = `<img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab" style="height:20px; vertical-align:middle;"/>`;

            actionHeader.insertBefore(btn, actionHeader.firstChild);
            console.log("✅ 'Open in Colab' button injected into GitHub DOM.");
        }
    }

    // Run on load and dynamic navigation
    addColabButton();
    const observer = new MutationObserver(addColabButton);
    observer.observe(document.body, { childList: true, subtree: true });
})();
