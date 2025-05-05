(() => {
  'use strict';

  document.addEventListener('DOMContentLoaded', () => {

    const ageSelect        = document.getElementById('age');
    const questionTextarea = document.getElementById('question');
    const questionForm     = document.querySelector('.question-form');
    const languageInput    = document.getElementById('language-input');
    const micButton        = document.getElementById('mic-button');
    const playButton       = document.getElementById('play-response');


    const errorContainer = document.createElement('div');
    errorContainer.setAttribute('aria-live', 'assertive');
    errorContainer.className = 'form-error';
    if (questionForm) questionForm.prepend(errorContainer);


    if (ageSelect) {
      try {
        const saved = localStorage.getItem('kidsgpt_age');
        if (saved) ageSelect.value = saved;
      } catch {}
      ageSelect.addEventListener('change', () => {
        try { localStorage.setItem('kidsgpt_age', ageSelect.value); } catch {}
      });
    }


    if (questionTextarea) {
      const adjust = () => {
        questionTextarea.style.height = 'auto';
        questionTextarea.style.height = questionTextarea.scrollHeight + 'px';
      };
      questionTextarea.addEventListener('input', adjust);
      if (questionTextarea.value) adjust();
    }


    if (questionForm) {
      questionForm.addEventListener('submit', e => {
        errorContainer.textContent = '';
        const langTr = languageInput.value === 'tr';
        const age    = ageSelect.value;
        const q      = questionTextarea.value.trim();

        if (!age) {
          e.preventDefault();
          errorContainer.textContent = langTr
            ? 'Lütfen yaşınızı seçin.'
            : 'Please select your age.';
          return;
        }
        if (!q) {
          e.preventDefault();
          errorContainer.textContent = langTr
            ? 'Lütfen bir soru girin.'
            : 'Please enter a question.';
          return;
        }

        const btn = questionForm.querySelector('button[type="submit"]');
        if (btn) {
          btn.disabled    = true;
          btn.textContent = langTr ? 'Düşünüyor...' : 'Thinking...';
        }
      });
    }


    new MutationObserver((m, obs) => {
      const resp = document.querySelector('.response-container');
      if (resp) {
        resp.scrollIntoView({ behavior: 'smooth', block: 'start' });
        obs.disconnect();
      }
    }).observe(document.body, { childList: true, subtree: true });

    // ——— Speech-to-Text ———
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec && micButton) {
      const rec = new SpeechRec();
      rec.lang            = languageInput.value === 'tr' ? 'tr-TR' : 'en-US';
      rec.interimResults  = false;
      rec.maxAlternatives = 1;

      micButton.addEventListener('click', () => rec.start());
      rec.addEventListener('result', e => {
        questionTextarea.value = e.results[0][0].transcript;
        questionTextarea.dispatchEvent(new Event('input'));
      });
      rec.addEventListener('speechend', () => rec.stop());
      rec.addEventListener('error', e => {
        alert((languageInput.value === 'tr'
          ? 'Ses tanıma hatası: '
          : 'Speech recognition error: ') + e.error);
      });
    } else if (micButton) {
      micButton.disabled = true;
      console.warn('SpeechRecognition API desteklenmiyor.');
    }


    function listVoices() {
      const vs = window.speechSynthesis.getVoices();
      console.log('Available voices:', vs.map(v => `${v.name} (${v.lang})`));
      return vs;
    }

    window.speechSynthesis.onvoiceschanged = listVoices;
    let voices = listVoices();

    function getTurkishVoice() {
      voices = window.speechSynthesis.getVoices();
      // 1) Exact tr-TR
      let v = voices.find(v=>v.lang.toLowerCase()==='tr-tr');
      // 2) Başlangıcı tr- ile
      if (!v) v = voices.find(v=>v.lang.toLowerCase().startsWith('tr'));
      // 3) İsmi içinde "turk" geçiyorsa
      if (!v) v = voices.find(v=>v.name.toLowerCase().includes('turk'));
      return v;
    }

    function speak(text, langCode) {

      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        return;
      }
      const u = new SpeechSynthesisUtterance(text);
      u.lang = langCode;
      const trVoice = getTurkishVoice();
      if (langCode.startsWith('tr')) {
        if (trVoice) {
          u.voice = trVoice;
        } else {
          alert('⚠️ Sisteminizde Türkçe bir ses bulunamadı. Lütfen işletim sistemi ses ayarlarından "Turkish" sesi yükleyin.');
        }
      }
      window.speechSynthesis.speak(u);
    }

    if (playButton) {
      playButton.addEventListener('click', () => {
        const rc = document.querySelector('.response-content');
        if (!rc) {
          return alert(languageInput.value === 'tr'
            ? 'Önce bir soru sorun.'
            : 'Please ask a question first.');
        }
        const txt      = rc.innerText.trim();
        const langCode = 'tr-TR';
        speak(txt, langCode);
      });
    }
  });
})();