package com.rosybence.flashcards;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.speech.tts.Voice;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Shows the flashcard web app without needing Chrome, and gives it the phone's own
 * voices (TextToSpeech) and speech recognition through window.NativeApp.
 */
public class MainActivity extends Activity {
    private static final int MIC_REQUEST = 1;
    private static final String GOOGLE_TTS = "com.google.android.tts";

    private WebView web;
    private TextToSpeech tts;
    private volatile boolean ttsReady = false;
    /** True only while the page shown is the app's own page on its own site (checked on every page load). */
    private volatile boolean trusted = false;
    private SpeechRecognizer recognizer;
    private final Handler main = new Handler(Looper.getMainLooper());

    private String pendingLang;
    private String pendingId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);

        web.addJavascriptInterface(new Bridge(), "NativeApp");
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, android.graphics.Bitmap favicon) {
                trusted = isOwnPage(url == null ? null : Uri.parse(url));
            }

            @Override
            public void doUpdateVisitedHistory(WebView view, String url, boolean isReload) {
                trusted = isOwnPage(url == null ? null : Uri.parse(url));
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (isOwnPage(u)) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
                return true;
            }
        });

        String engine = isInstalled(GOOGLE_TTS) ? GOOGLE_TTS : null;
        tts = new TextToSpeech(this, status -> {
            ttsReady = status == TextToSpeech.SUCCESS;
            if (ttsReady) js("window.__nativeTtsReady&&window.__nativeTtsReady()");
        }, engine);
        tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override public void onStart(String id) { }
            @Override public void onDone(String id) { ttsDone(id); }
            @Override public void onError(String id) { ttsDone(id); }
            @Override public void onStop(String id, boolean interrupted) { ttsDone(id); }
        });

        if (savedInstanceState == null) web.loadUrl(BuildConfig.START_URL);
        else web.restoreState(savedInstanceState);
    }

    /** Only https pages inside this app's folder on rosybence.github.io may use the microphone and voices. */
    private static boolean isOwnPage(Uri u) {
        if (u == null) return false;
        String path = u.getPath() == null ? "" : u.getPath();
        return "https".equals(u.getScheme()) && "rosybence.github.io".equals(u.getHost()) && path.startsWith(BuildConfig.SCOPE);
    }

    private boolean isInstalled(String pkg) {
        try { getPackageManager().getPackageInfo(pkg, 0); return true; } catch (Exception e) { return false; }
    }

    private void js(String code) {
        main.post(() -> { if (web != null) web.evaluateJavascript(code, null); });
    }

    private void ttsDone(String id) {
        js("window.__nativeTtsDone&&window.__nativeTtsDone(" + JSONObject.quote(id) + ")");
    }

    private void srCallback(String id, String kind, String json) {
        js("window.__nativeSr&&window.__nativeSr(" + JSONObject.quote(id) + "," + JSONObject.quote(kind) + "," + json + ")");
    }

    private static String firstResult(Bundle b) {
        ArrayList<String> r = b == null ? null : b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
        return r == null || r.isEmpty() ? "" : r.get(0);
    }

    private void startListening(String lang, String id) {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            pendingLang = lang; pendingId = id;
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, MIC_REQUEST);
            return;
        }
        if (recognizer != null) { recognizer.destroy(); recognizer = null; }
        if (!SpeechRecognizer.isRecognitionAvailable(this)) { srCallback(id, "error", "\"unavailable\""); return; }
        recognizer = SpeechRecognizer.createSpeechRecognizer(this);
        final String rid = id;
        recognizer.setRecognitionListener(new RecognitionListener() {
            @Override public void onReadyForSpeech(Bundle params) { }
            @Override public void onBeginningOfSpeech() { }
            @Override public void onRmsChanged(float rmsdB) { }
            @Override public void onBufferReceived(byte[] buffer) { }
            @Override public void onEndOfSpeech() { }
            @Override public void onEvent(int eventType, Bundle params) { }
            @Override public void onPartialResults(Bundle b) {
                srCallback(rid, "partial", JSONObject.quote(firstResult(b)));
            }
            @Override public void onResults(Bundle b) {
                ArrayList<String> r = b == null ? null : b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION);
                srCallback(rid, "result", new JSONArray(r == null ? new ArrayList<String>() : r).toString());
            }
            @Override public void onError(int error) {
                String code;
                if (error == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) code = "not-allowed";
                else if (error == SpeechRecognizer.ERROR_NO_MATCH || error == SpeechRecognizer.ERROR_SPEECH_TIMEOUT) code = "no-speech";
                else code = "error-" + error;
                srCallback(rid, "error", JSONObject.quote(code));
            }
        });
        Intent i = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, lang);
        i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true);
        i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5);
        i.putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, getPackageName());
        recognizer.startListening(i);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        if (requestCode != MIC_REQUEST || pendingId == null) return;
        String lang = pendingLang, id = pendingId;
        pendingLang = null; pendingId = null;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED) startListening(lang, id);
        else srCallback(id, "error", "\"not-allowed\"");
    }

    private Voice findVoice(String name) {
        if (name == null || name.isEmpty() || !ttsReady) return null;
        try {
            for (Voice v : tts.getVoices()) if (name.equals(v.getName())) return v;
        } catch (Exception ignored) { }
        return null;
    }

    private void applyImmersive(boolean on) {
        View d = getWindow().getDecorView();
        d.setSystemUiVisibility(on
                ? View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN
                  | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                : View.SYSTEM_UI_FLAG_VISIBLE);
    }

    /** Methods the web page can call as window.NativeApp.* */
    private class Bridge {
        @JavascriptInterface public boolean srAvailable() {
            if (!trusted) return false;
            return SpeechRecognizer.isRecognitionAvailable(MainActivity.this);
        }

        @JavascriptInterface public void speak(String text, String lang, float rate, String id, String voiceName) {
            if (!trusted) return;
            main.post(() -> {
                if (!ttsReady) { ttsDone(id); return; }
                Voice v = findVoice(voiceName);
                if (v != null) tts.setVoice(v); else tts.setLanguage(Locale.forLanguageTag(lang));
                tts.setSpeechRate(rate);
                if (tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, id) != TextToSpeech.SUCCESS) ttsDone(id);
            });
        }

        @JavascriptInterface public void stopSpeaking() {
            if (!trusted) return;
            main.post(() -> { if (tts != null) tts.stop(); });
        }

        /** Installed voices for a language ("ja", "es", "en"), best quality first. */
        @JavascriptInterface public String voices(String prefix) {
            if (!trusted) return "[]";
            JSONArray out = new JSONArray();
            if (!ttsReady) return out.toString();
            try {
                Set<Voice> all = tts.getVoices();
                List<Voice> list = new ArrayList<>();
                for (Voice v : all) {
                    if (!v.getLocale().getLanguage().equalsIgnoreCase(prefix)) continue;
                    Set<String> f = v.getFeatures();
                    if (f != null && f.contains(TextToSpeech.Engine.KEY_FEATURE_NOT_INSTALLED)) continue;
                    list.add(v);
                }
                Collections.sort(list, (a, b) -> {
                    int q = Integer.compare(b.getQuality(), a.getQuality());
                    if (q != 0) return q;
                    int c = a.getLocale().toString().compareTo(b.getLocale().toString());
                    return c != 0 ? c : a.getName().compareTo(b.getName());
                });
                int n = 0;
                for (Voice v : list) {
                    Locale l = v.getLocale();
                    String place = l.getDisplayCountry(Locale.UK);
                    String label = l.getDisplayLanguage(Locale.UK) + (place.isEmpty() ? "" : " (" + place + ")")
                            + " · voice " + (++n)
                            + (v.isNetworkConnectionRequired() ? " · online" : " · offline")
                            + (v.getQuality() >= Voice.QUALITY_HIGH ? " · high quality" : "");
                    JSONObject o = new JSONObject();
                    o.put("name", v.getName());
                    o.put("label", label);
                    out.put(o);
                }
            } catch (Exception ignored) { }
            return out.toString();
        }

        @JavascriptInterface public void listen(String lang, String id) {
            if (!trusted) return;
            main.post(() -> startListening(lang, id));
        }

        @JavascriptInterface public void stopListening() {
            if (!trusted) return;
            main.post(() -> { if (recognizer != null) recognizer.stopListening(); });
        }

        @JavascriptInterface public void abortListening() {
            if (!trusted) return;
            main.post(() -> { if (recognizer != null) recognizer.cancel(); });
        }

        @JavascriptInterface public void keepAwake(boolean on) {
            if (!trusted) return;
            main.post(() -> {
                if (on) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            });
        }

        @JavascriptInterface public void immersive(boolean on) {
            if (!trusted) return;
            main.post(() -> applyImmersive(on));
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override
    protected void onDestroy() {
        if (tts != null) tts.shutdown();
        if (recognizer != null) recognizer.destroy();
        if (web != null) web.destroy();
        super.onDestroy();
    }
}
