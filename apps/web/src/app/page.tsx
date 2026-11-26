"use client";

import React, { useState, useRef, useMemo, useEffect } from "react";
import {
  ApiClient,
  DEFAULT_PROJECT_ID,
  AnalysisResult,
  RewriteResult,
  DimensionScore,
  TaxonomyTag,
  EvidenceQuote,
} from "../lib/api";
import {
  Plus,
  Menu,
  X,
  Copy,
  Check,
  Trash2,
  ExternalLink,
  Activity,
  Layers,
  Sparkles,
  ArrowRight,
  ChevronRight,
  BookOpen,
  Download,
  AlertCircle,
  Folder,
  History,
  CornerDownLeft,
  Sliders,
  Maximize2,
  FileText,
} from "lucide-react";

interface PresetScene {
  id: string;
  title: string;
  genre: string;
  tensionLevel: string;
  content: string;
}

const PRESET_SCENES: PresetScene[] = [
  {
    id: "arctic-vault",
    title: "Arctic Vault Cutoff",
    genre: "Sci-Fi / Thriller",
    tensionLevel: "High Tension",
    content: `INT. ARCTIC VAULT - NIGHT

Dr. Marcus Kane reached the bio-vault emergency console with his hands shaking in chemical burns. Behind him, the reinforced blast glass began spider-webbing under hydraulic pressure. He slotted the master override key, but the screen turned crimson. The automated defense voice echoed: 'Primary quarantine breached. Complete thermal purge initiated. T-minus ten seconds. Escape pods jettisoned.'`,
  },
  {
    id: "neo-seoul",
    title: "Catwalk Leap Dilemma",
    genre: "Cyberpunk Action",
    tensionLevel: "Extreme Peril",
    content: `EXT. UPPER NEO-SEOUL CATWALK - NIGHT

Kira ripped the encrypted cortex drive from the server column. The magnetic boots of corporate security slammed onto the grating ten meters above. Her earpiece hissed with Mercer's voice: 'I cut the district power grid for three seconds, Kira. If you jump right now, you land on the hover-freighter. If you miss, it's eight hundred meters of empty rain.' Below her, the streetlights flickered and died.`,
  },
  {
    id: "ravenscroft",
    title: "The Cellar Heirlooms",
    genre: "Gothic Mystery",
    tensionLevel: "Dark Revelation",
    content: `INT. RAVENSCROFT MANOR - MIDNIGHT

Eleanor held the brass lantern high against the damp cellar wall. Behind the dislodged hearthstones lay a velvet jewelry case, undisturbed since 1894. With trembling fingers she pried open the rusted latch. Inside was not the family diamond, but a pair of blood-stained surgical shears and an unsealed letter addressed to her in her father's handwriting—postmarked this morning.`,
  },
  {
    id: "bistro-flat",
    title: "Afternoon Coffee",
    genre: "Contemporary Drama",
    tensionLevel: "Resolved / Flat",
    content: `INT. BISTRO - AFTERNOON

David finished his cappuccino and placed the exact change on the polished mahogany bar. Outside, golden autumn leaves drifted lazily across the sunlit sidewalk. He smiled warmly at the barista, adjusted his wool scarf, and walked leisurely toward the subway station. The dispute was settled, the paperwork filed, and for the first time in fifteen years, he had nowhere he needed to be.`,
  },
];

interface DimensionMeta {
  label: string;
  description: string;
  focusHint: string;
}

const DIMENSION_METADATA: Record<string, DimensionMeta> = {
  unresolved_question: {
    label: "Unresolved Question",
    description: "The core narrative question or mystery left hanging to hook reader curiosity.",
    focusHint: "Leave an acute question without immediate answer right before cutting the scene.",
  },
  stakes: {
    label: "Narrative Stakes",
    description: "Severity of imminent physical, emotional, or existential loss.",
    focusHint: "Ensure the character has everything to lose in the very next beat.",
  },
  emotional_intensity: {
    label: "Emotional Intensity",
    description: "Peak dread, shock, heartbreak, or arousal created right at the cutoff.",
    focusHint: "Heighten visceral emotional beats in the final sentences.",
  },
  character_consequence: {
    label: "Character Consequence",
    description: "Impact on protagonist trajectory, status, moral standing, or survival.",
    focusHint: "Force a permanent shift in character state or relationships.",
  },
  surprise: {
    label: "Surprise & Subversion",
    description: "An unexpected turn that challenges reader assumptions while feeling earned.",
    focusHint: "Subvert reader expectations logically with an unpredicted obstacle.",
  },
  urgency: {
    label: "Urgency & Pacing",
    description: "Immediate time sensitivity, ticking clock, or forced dilemma.",
    focusHint: "Add an unyielding countdown or compressed window for decision.",
  },
  causal_setup: {
    label: "Causal Continuity",
    description: "How logically the ending is earned from prior story events and character actions.",
    focusHint: "Ground the cliffhanger in established narrative rules and causes.",
  },
  information_gap: {
    label: "Information Gap",
    description: "Tension between what the reader knows versus what the characters know.",
    focusHint: "Reveal a crucial piece of knowledge to the reader or character alone.",
  },
  originality: {
    label: "Freshness of Execution",
    description: "Distinctive narrative punch avoiding predictable tropes or cliché exhaustion.",
    focusHint: "Avoid formulaic cliché phrases; sharpen imagery and unique voice.",
  },
};

interface BandMeta {
  label: string;
  badgeClass: string;
  symbol: string;
  explanation: string;
}

const SCORE_BAND_METADATA: Record<string, BandMeta> = {
  Exceptional: {
    label: "Exceptional Cliffhanger",
    badgeClass: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    symbol: "★",
    explanation: "Masterful chapter cutoff delivering peak tension, visceral stakes, and an irresistible compulsion to continue reading.",
  },
  "Very Strong": {
    label: "Very Strong Hook",
    badgeClass: "bg-blue-500/10 text-blue-400 border-blue-500/30",
    symbol: "◆",
    explanation: "Highly compelling cliffhanger with immediate urgency, major open questions, or a potent dramatic reveal.",
  },
  Strong: {
    label: "Strong Cliffhanger",
    badgeClass: "bg-sky-500/10 text-sky-400 border-sky-500/30",
    symbol: "▲",
    explanation: "Effective scene ending with tangible narrative momentum and clear unanswered stakes.",
  },
  Moderate: {
    label: "Moderate Suspense",
    badgeClass: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    symbol: "●",
    explanation: "Functional ending, but stakes or immediate time pressure could be intensified to create a true page-turner.",
  },
  Weak: {
    label: "Weak Ending Hook",
    badgeClass: "bg-rose-500/10 text-rose-400 border-rose-500/30",
    symbol: "■",
    explanation: "Low narrative tension. The scene concludes with premature resolution or lacks urgency to pull the reader forward.",
  },
  "No Meaningful Cliffhanger": {
    label: "Resolved / Low Tension",
    badgeClass: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
    symbol: "○",
    explanation: "The ending feels closed or completely resolved without unanswered questions driving the plot.",
  },
};

const TAXONOMY_LABELS: Record<string, string> = {
  threat: "Imminent Danger",
  countdown: "Ticking Clock",
  revelation: "Shocking Revelation",
  decision: "Irrevocable Choice",
  identity: "Secret Identity",
  relationship: "Interpersonal Fracture",
  mission: "Mission Objective Shift",
  moral: "Moral Dilemma",
  reversal: "Power Reversal",
  mystery: "Baffling Mystery",
  parallel: "Simultaneous Cutoff",
  existential: "Existential Peril",
};

interface HistoryItem {
  id: string;
  title: string;
  timestamp: string;
  score: number;
  scoreBand: string;
  inputText: string;
  result: AnalysisResult;
}

export default function CodexCliffhangerWorkspace() {
  const [inputText, setInputText] = useState(PRESET_SCENES[0].content);
  const [sceneTitle, setSceneTitle] = useState(PRESET_SCENES[0].title);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"dimensions" | "evidence" | "rewrite" | "report">("dimensions");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // History state
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Rewrite state
  const [targetDim, setTargetDim] = useState<string>("urgency");
  const [rewriting, setRewriting] = useState(false);
  const [rewriteResult, setRewriteResult] = useState<RewriteResult | null>(null);
  const [analysisRewrites, setAnalysisRewrites] = useState<Record<string, RewriteResult>>({});
  const [isRewriteDemo, setIsRewriteDemo] = useState(false);
  const [rewriteError, setRewriteError] = useState<string | null>(null);

  // Interaction helpers
  const [selectedQuote, setSelectedQuote] = useState<string | null>(null);
  const [quoteMatchStatus, setQuoteMatchStatus] = useState<"matched" | "not_found" | null>(null);
  const [copiedRewrite, setCopiedRewrite] = useState(false);
  const [copiedInput, setCopiedInput] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);
  const [pasteNotice, setPasteNotice] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load history from localStorage on initial mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("cliffhanger_analysis_history");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          setHistory(parsed.slice(0, 15));
        }
      }
    } catch {
      // Storage unavailable or invalid
    }
  }, []);

  // Save history to localStorage
  const saveHistoryItem = (item: HistoryItem) => {
    setHistory((prev) => {
      const updated = [item, ...prev.filter((h) => h.id !== item.id)].slice(0, 15);
      try {
        localStorage.setItem("cliffhanger_analysis_history", JSON.stringify(updated));
      } catch {
        // Ignore
      }
      return updated;
    });
  };

  const clearHistory = () => {
    setHistory([]);
    try {
      localStorage.removeItem("cliffhanger_analysis_history");
    } catch {
      // Ignore
    }
  };

  // Word & character stats
  const stats = useMemo(() => {
    const trimmed = inputText.trim();
    const words = trimmed ? trimmed.split(/\s+/).filter(Boolean).length : 0;
    const chars = inputText.length;
    return { words, chars };
  }, [inputText]);

  // Identify lowest scoring dimension to recommend
  const lowestScoringDimension = useMemo(() => {
    if (!result?.dimension_breakdown || result.dimension_breakdown.length === 0) {
      return null;
    }
    const sorted = [...result.dimension_breakdown].sort((a, b) => a.score - b.score);
    return sorted[0];
  }, [result]);

  const handleNewAnalysis = () => {
    setInputText("");
    setSceneTitle("New Scene Ending");
    setResult(null);
    setRewriteResult(null);
    setErrorMessage(null);
    setSelectedQuote(null);
    setQuoteMatchStatus(null);
    setActiveTab("dimensions");
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
    setSidebarOpen(false);
  };

  const handleLoadPreset = (preset: PresetScene) => {
    setInputText(preset.content);
    setSceneTitle(preset.title);
    setResult(null);
    setRewriteResult(null);
    setErrorMessage(null);
    setSelectedQuote(null);
    setQuoteMatchStatus(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
    setSidebarOpen(false);
  };

  const handleSelectHistory = (item: HistoryItem) => {
    setInputText(item.inputText);
    setSceneTitle(item.title);
    setResult(item.result);
    setRewriteResult(analysisRewrites[item.id] || null);
    setSelectedQuote(null);
    setQuoteMatchStatus(null);
    setSidebarOpen(false);
  };

  const handleClear = () => {
    setInputText("");
    setResult(null);
    setRewriteResult(null);
    setErrorMessage(null);
    setSelectedQuote(null);
    setQuoteMatchStatus(null);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handlePasteClipboard = async () => {
    try {
      if (typeof navigator !== "undefined" && navigator.clipboard?.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setInputText((prev) => (prev ? `${prev}\n\n${text}` : text));
          setPasteNotice("Text pasted from clipboard");
          setTimeout(() => setPasteNotice(null), 2500);
        }
      } else {
        setPasteNotice("Use Cmd+V / Ctrl+V to paste");
        setTimeout(() => setPasteNotice(null), 2500);
      }
    } catch {
      setPasteNotice("Clipboard access blocked. Use Cmd+V / Ctrl+V.");
      setTimeout(() => setPasteNotice(null), 3000);
    }
  };

  const handleCopyInput = async () => {
    if (!inputText) return;
    try {
      await navigator.clipboard.writeText(inputText);
      setCopiedInput(true);
      setTimeout(() => setCopiedInput(false), 2000);
    } catch {
      // Fallback ignored
    }
  };

  const handleAnalyze = async () => {
    const textToAnalyze = inputText.trim();
    if (!textToAnalyze) return;

    setAnalyzing(true);
    setErrorMessage(null);
    setRewriteResult(null);
    setSelectedQuote(null);
    setQuoteMatchStatus(null);

    try {
      const data = await ApiClient.analyzeText(DEFAULT_PROJECT_ID, textToAnalyze);
      setResult(data);
      setIsDemoMode(false);

      if (data.dimension_breakdown && data.dimension_breakdown.length > 0) {
        const sorted = [...data.dimension_breakdown].sort((a, b) => a.score - b.score);
        setTargetDim(sorted[0].dimension_name);
      }

      // Record in history
      saveHistoryItem({
        id: data.analysis_id || "analysis-" + Date.now(),
        title: sceneTitle || "Ending Analysis",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        score: data.final_score,
        scoreBand: data.score_band,
        inputText: textToAnalyze,
        result: data,
      });
    } catch {
      // Offline fallback
      setIsDemoMode(true);
      simulateDemoAnalysis(textToAnalyze);
    } finally {
      setAnalyzing(false);
    }
  };

  const simulateDemoAnalysis = (text: string) => {
    const textLower = text.toLowerCase();
    const hasCountdown =
      textLower.includes("second") ||
      textLower.includes("countdown") ||
      textLower.includes("time") ||
      textLower.includes("timer") ||
      textLower.includes("00:0");
    const hasDanger =
      textLower.includes("breach") ||
      textLower.includes("burn") ||
      textLower.includes("blast") ||
      textLower.includes("die") ||
      textLower.includes("kill") ||
      textLower.includes("jump") ||
      textLower.includes("blood");
    const hasMystery =
      textLower.includes("secret") ||
      textLower.includes("letter") ||
      textLower.includes("case") ||
      textLower.includes("unopened") ||
      textLower.includes("father") ||
      textLower.includes("unknown");
    const isFlat = textLower.includes("finished") && textLower.includes("leisurely") && textLower.includes("nowhere");

    let baseScore = 65.0;
    if (isFlat) {
      baseScore = 32.5;
    } else if (hasCountdown && hasDanger) {
      baseScore = 87.2;
    } else if (hasDanger || hasMystery) {
      baseScore = 78.4;
    }

    const band =
      baseScore >= 90
        ? "Exceptional"
        : baseScore >= 80
        ? "Very Strong"
        : baseScore >= 65
        ? "Strong"
        : baseScore >= 50
        ? "Moderate"
        : "Weak";

    const demoResult: AnalysisResult = {
      analysis_id: "demo-" + Math.random().toString(36).substring(2, 9),
      project_id: DEFAULT_PROJECT_ID,
      asset_id: "demo-asset-01",
      final_score: baseScore,
      score_band: band,
      dimension_breakdown: [
        {
          dimension_name: "unresolved_question",
          score: isFlat ? 25 : hasMystery ? 92 : hasDanger ? 88 : 70,
          weight: 0.2,
          weighted_contribution: isFlat ? 5.0 : hasMystery ? 18.4 : 17.6,
          confidence: 0.92,
          explanation: isFlat
            ? "No significant narrative questions remain unanswered at the cutoff."
            : "Acute survival and identity questions are left hanging directly over the character.",
        },
        {
          dimension_name: "stakes",
          score: isFlat ? 20 : hasDanger ? 92 : 72,
          weight: 0.15,
          weighted_contribution: isFlat ? 3.0 : 13.8,
          confidence: 0.95,
          explanation: isFlat
            ? "Consequences are neutral with no impending loss or risk."
            : "Mortal peril or devastating personal revelation imminent if the protagonist fails.",
        },
        {
          dimension_name: "emotional_intensity",
          score: isFlat ? 30 : hasDanger ? 89 : 76,
          weight: 0.15,
          weighted_contribution: isFlat ? 4.5 : 13.35,
          confidence: 0.9,
          explanation: isFlat
            ? "Scene tone is tranquil with settled emotions."
            : "Visceral dread and surging adrenaline generated right at the closing beat.",
        },
        {
          dimension_name: "character_consequence",
          score: isFlat ? 35 : 82,
          weight: 0.1,
          weighted_contribution: isFlat ? 3.5 : 8.2,
          confidence: 0.85,
          explanation: isFlat
            ? "Character status quo is preserved comfortably."
            : "Direct irreversible impact on the protagonist's trajectory and physical safety.",
        },
        {
          dimension_name: "surprise",
          score: isFlat ? 30 : 79,
          weight: 0.1,
          weighted_contribution: isFlat ? 3.0 : 7.9,
          confidence: 0.82,
          explanation: isFlat
            ? "Ending proceeds strictly according to everyday expectations."
            : "Abrupt reversal or shocking discovery subverts safe outcomes.",
        },
        {
          dimension_name: "urgency",
          score: isFlat ? 20 : hasCountdown ? 94 : 68,
          weight: 0.1,
          weighted_contribution: isFlat ? 2.0 : hasCountdown ? 9.4 : 6.8,
          confidence: 0.94,
          explanation: isFlat
            ? "No time limitation exists to pressure character action."
            : hasCountdown
            ? "Active ticking clock with less than ten seconds to avert catastrophe."
            : "Moderate narrative momentum.",
        },
        {
          dimension_name: "causal_setup",
          score: isFlat ? 80 : 85,
          weight: 0.1,
          weighted_contribution: isFlat ? 8.0 : 8.5,
          confidence: 0.88,
          explanation: "Ending flows logically from the chain of preceding character decisions.",
        },
        {
          dimension_name: "information_gap",
          score: isFlat ? 30 : hasMystery ? 90 : 74,
          weight: 0.05,
          weighted_contribution: isFlat ? 1.5 : hasMystery ? 4.5 : 3.7,
          confidence: 0.8,
          explanation: hasMystery
            ? "Asymmetry between reader knowledge and hidden truths creates keen suspense."
            : "Audience witnesses the cliffhanger beat synchronously with the protagonist.",
        },
        {
          dimension_name: "originality",
          score: isFlat ? 45 : 78,
          weight: 0.05,
          weighted_contribution: isFlat ? 2.25 : 3.9,
          confidence: 0.8,
          explanation: "Effective craft execution avoiding tired formulaic tropes.",
        },
      ],
      taxonomy_classifications: [
        ...(hasDanger ? [{ type: "threat", confidence: 0.95, rationale: "Direct physical peril locks character in." }] : []),
        ...(hasCountdown ? [{ type: "countdown", confidence: 0.92, rationale: "Explicit temporal countdown before destruction." }] : []),
        ...(hasMystery ? [{ type: "mystery", confidence: 0.91, rationale: "Unsettling artifact raises unanswered questions." }] : []),
        ...(!hasDanger && !hasMystery && !isFlat ? [{ type: "decision", confidence: 0.8, rationale: "Forced dilemma with no safe choices." }] : []),
        ...(isFlat ? [{ type: "resolution", confidence: 0.98, rationale: "Complete peaceful closure with no open loops." }] : []),
      ],
      evidence_quotes: [
        {
          quote: text.split("\n\n").pop() || text.slice(-120),
          location: "Closing cutoff beat",
          relevance: 0.98,
        },
      ],
      open_questions: isFlat
        ? ["Will the character find new motivations in subsequent scenes?"]
        : [
            "Can the protagonist evade catastrophic consequences before time expires?",
            "What hidden conspiracy or secondary threat triggered this cutoff sequence?",
          ],
      model_name: "calibrated-heuristic-engine",
      prompt_version: "v1.0.0",
    };

    setResult(demoResult);

    const sorted = [...demoResult.dimension_breakdown].sort((a, b) => a.score - b.score);
    setTargetDim(sorted[0].dimension_name);

    saveHistoryItem({
      id: demoResult.analysis_id,
      title: sceneTitle || "Ending Analysis",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      score: demoResult.final_score,
      scoreBand: demoResult.score_band,
      inputText: text,
      result: demoResult,
    });
  };

  const handleQuoteClick = (quoteText: string) => {
    setSelectedQuote(quoteText);

    if (!textareaRef.current) return;

    const editorText = inputText;
    let matchIdx = editorText.indexOf(quoteText);
    let matchLen = quoteText.length;

    if (matchIdx === -1) {
      const lowerEditor = editorText.toLowerCase();
      const lowerQuote = quoteText.toLowerCase();
      matchIdx = lowerEditor.indexOf(lowerQuote);
      if (matchIdx === -1) {
        const snippet = lowerQuote.slice(0, 25);
        matchIdx = lowerEditor.indexOf(snippet);
        if (matchIdx !== -1) {
          matchLen = Math.min(quoteText.length, editorText.length - matchIdx);
        }
      }
    }

    if (matchIdx !== -1) {
      setQuoteMatchStatus("matched");
      textareaRef.current.focus();
      textareaRef.current.setSelectionRange(matchIdx, matchIdx + matchLen);
      textareaRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    } else {
      setQuoteMatchStatus("not_found");
    }
  };

  const handleRewrite = async () => {
    if (!result) return;

    setRewriting(true);
    setRewriteError(null);
    setCopiedRewrite(false);

    const isLive = !isDemoMode && result.analysis_id && !result.analysis_id.startsWith("demo-");

    if (isLive) {
      try {
        const rewrite = await ApiClient.requestRewrite(result.analysis_id, targetDim, "intensified", inputText);
        setRewriteResult(rewrite);
        setAnalysisRewrites((prev) => ({ ...prev, [result.analysis_id]: rewrite }));
        setIsRewriteDemo(false);
      } catch (err: any) {
        setRewriteError(err.message || "Failed to generate alternative ending.");
      } finally {
        setRewriting(false);
      }
    } else {
      simulateDemoRewrite(targetDim);
      setRewriting(false);
    }
  };

  const simulateDemoRewrite = (dimension: string) => {
    setIsRewriteDemo(true);

    const baselineScore = result?.final_score || 64.0;
    const boost = 14.5;
    const predicted = Math.min(99.0, Number((baselineScore + boost).toFixed(1)));
    const lower = inputText.toLowerCase();

    let rewriteBody = "";
    if (lower.includes("arjun") || lower.includes("meera") || lower.includes("door 17")) {
      if (dimension === "urgency") {
        rewriteBody = `${inputText.trim()}\n\nArjun stepped back from the reinforced glass of Door 17 as the monitor flared crimson. Dr. Meera's security badge slipped from his fingers—the terminal access log showed she had already logged into the inner laboratory sixty seconds before he arrived.`;
      } else if (dimension === "stakes") {
        rewriteBody = `${inputText.trim()}\n\nArjun gripped the cold steel handle of Door 17 as the thermal seal disengaged. The duplicate identity card inside the terminal wasn't an unauthorized counterfeit—it belonged to him, stamped with tomorrow's expiration date.`;
      } else {
        rewriteBody = `${inputText.trim()}\n\nDr. Meera reached toward the manual release valve for Door 17, but froze mid-motion. 'Arjun,' she whispered, staring at the bioscan readout on the console, 'if you are standing right in front of me... whose voice is answering from the intercom inside the vault?'`;
      }
    } else if (lower.includes("riya") || lower.includes("aarav") || lower.includes("mother") || lower.includes("blue box")) {
      if (dimension === "urgency") {
        rewriteBody = `${inputText.trim()}\n\nA sudden silence gripped the room as Riya's hands trembled against the brass clasp of the blue box. Aarav stepped forward, pointing at the heart monitor as the digital pulse line flattened for two agonizing seconds before catching again.`;
      } else if (dimension === "stakes") {
        rewriteBody = `${inputText.trim()}\n\nRiya pressed the folded letter into Aarav's hand, her voice barely a whisper. 'The memory restoration didn't fail,' she said, looking down at their mother. 'She remembers everything—including why she had our childhood records erased.'`;
      } else {
        rewriteBody = `${inputText.trim()}\n\nAarav lifted the silver frame from the hospital bedside table, turning the photograph toward the light. Standing directly behind their mother's smiling portrait was a third figure holding the identical blue box—someone neither of them had ever seen.`;
      }
    } else {
      rewriteBody = `${inputText.trim()}\n\nA heavy silence settled over the room as the realization took hold. The dilemma wasn't what had just transpired—it was what had to be done next.`;
    }

    const demoRewrite: RewriteResult = {
      rewrite_id: "demo-rewrite-" + Math.random().toString(36).substring(2, 9),
      analysis_id: result?.analysis_id || "demo-analysis",
      target_dimension: dimension,
      original_score: baselineScore,
      predicted_score: predicted,
      score_delta: boost,
      content: rewriteBody,
      is_consistent: true,
      validation_critique: "Maintains established scene facts and character continuity.",
    };

    setRewriteResult(demoRewrite);
    if (result?.analysis_id) {
      setAnalysisRewrites((prev) => ({ ...prev, [result.analysis_id]: demoRewrite }));
    }
  };

  const handleCopyRewrite = async () => {
    if (!rewriteResult?.content) return;
    try {
      await navigator.clipboard.writeText(rewriteResult.content);
      setCopiedRewrite(true);
      setTimeout(() => setCopiedRewrite(false), 2000);
    } catch {
      // Ignore
    }
  };

  const handleApplyRewriteToInput = () => {
    if (!rewriteResult?.content) return;
    setInputText(rewriteResult.content);
    setResult(null);
    setRewriteResult(null);
    setSelectedQuote(null);
    setQuoteMatchStatus(null);
    setActiveTab("dimensions");
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleCopyReport = async () => {
    if (!result) return;
    const report = `# Cliffhanger Strength Evaluation Report
Scene: ${sceneTitle}
Overall Score: ${result.final_score.toFixed(1)} / 100 (${result.score_band})
Engine: ${result.model_name}

## 9 Dimension Breakdown:
${result.dimension_breakdown
  .map(
    (d) =>
      `- ${DIMENSION_METADATA[d.dimension_name]?.label || d.dimension_name}: ${d.score.toFixed(1)}/100 (Weight: ${(
        d.weight * 100
      ).toFixed(0)}%) - ${d.explanation}`
  )
  .join("\n")}

## Unresolved Questions:
${result.open_questions.map((q) => `- ${q}`).join("\n")}

## Ending Excerpt:
${inputText}
`;
    try {
      await navigator.clipboard.writeText(report);
      setCopiedReport(true);
      setTimeout(() => setCopiedReport(false), 2000);
    } catch {
      // Ignore
    }
  };

  // Keyboard shortcut: Ctrl+Enter / Cmd+Enter to analyze
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (inputText.trim() && !analyzing) {
        handleAnalyze();
      }
    }
  };

  const bandMeta = result
    ? SCORE_BAND_METADATA[result.score_band] || {
        label: result.score_band,
        badgeClass: "bg-zinc-800 text-zinc-300 border-zinc-700",
        symbol: "●",
        explanation: "Narrative cliffhanger evaluation completed.",
      }
    : null;

  return (
    <div className="flex h-screen w-full bg-[#0d0d0f] text-[#ececee] font-sans antialiased overflow-hidden">
      {/* =========================================================================
          LEFT SIDEBAR: Fixed Codex Desktop Sidebar (Dark Charcoal #131315)
         ========================================================================= */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 bg-[#131315] border-r border-[#222227] flex flex-col transition-transform duration-200 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* App Title Header */}
        <div className="h-14 px-4 border-b border-[#222227] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-[#1f1f24] border border-[#2d2d35] flex items-center justify-center text-blue-400 font-semibold text-xs shadow-inner">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-semibold text-sm tracking-tight text-white">Cliffhanger</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#1e2029] text-blue-400 font-mono border border-blue-500/20">
                  v1.0
                </span>
              </div>
              <span className="text-[11px] text-[#858592] block leading-none">Suspense & Tension Lab</span>
            </div>
          </div>

          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1.5 rounded-md hover:bg-[#1f1f24] text-[#8e8e99] hover:text-white"
            aria-label="Close sidebar"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Primary "+ New analysis" Action */}
        <div className="p-3">
          <button
            type="button"
            onClick={handleNewAnalysis}
            className="w-full py-2 px-3 rounded-lg bg-[#18181c] hover:bg-[#202026] text-white border border-[#282830] hover:border-[#383844] font-medium text-xs flex items-center justify-between transition group shadow-sm"
          >
            <div className="flex items-center gap-2">
              <Plus className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
              <span>New analysis</span>
            </div>
            <span className="text-[10px] text-[#71717e] font-mono px-1 rounded bg-[#131316] border border-[#232328]">
              Ctrl+N
            </span>
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-5">
          {/* Section: Preset Scenes */}
          <div>
            <div className="flex items-center justify-between px-2 mb-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#737380] flex items-center gap-1.5">
                <Folder className="w-3 h-3 text-[#52525c]" />
                Preset Scenes
              </span>
              <span className="text-[10px] text-[#52525c] font-mono">{PRESET_SCENES.length}</span>
            </div>

            <div className="space-y-0.5">
              {PRESET_SCENES.map((preset) => {
                const isSelected = sceneTitle === preset.title && inputText === preset.content;
                return (
                  <button
                    key={preset.id}
                    type="button"
                    onClick={() => handleLoadPreset(preset)}
                    className={`w-full text-left px-2.5 py-2 rounded-lg text-xs transition flex items-center justify-between group ${
                      isSelected
                        ? "bg-[#1e2029] text-white font-medium border border-blue-500/30"
                        : "text-[#a1a1aa] hover:bg-[#1a1a1f] hover:text-[#e4e4e7]"
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="truncate">{preset.title}</div>
                      <div className="text-[10px] text-[#71717a] truncate font-mono mt-0.5">{preset.genre}</div>
                    </div>
                    <span
                      className={`text-[9px] px-1.5 py-0.5 rounded font-mono shrink-0 ${
                        preset.tensionLevel.includes("High") || preset.tensionLevel.includes("Extreme")
                          ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          : preset.tensionLevel.includes("Dark")
                          ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                          : "bg-zinc-800 text-zinc-400"
                      }`}
                    >
                      {preset.tensionLevel}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Section: Recent Analyses */}
          <div>
            <div className="flex items-center justify-between px-2 mb-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#737380] flex items-center gap-1.5">
                <History className="w-3 h-3 text-[#52525c]" />
                Recent Analyses
              </span>
              {history.length > 0 && (
                <button
                  type="button"
                  onClick={clearHistory}
                  className="text-[10px] text-[#71717a] hover:text-rose-400 transition"
                  title="Clear history"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div className="px-3 py-4 text-center rounded-lg border border-dashed border-[#232328] text-[11px] text-[#5b5b66]">
                Analyses you run will appear here.
              </div>
            ) : (
              <div className="space-y-0.5">
                {history.map((item) => {
                  const isActive = result?.analysis_id === item.result.analysis_id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => handleSelectHistory(item)}
                      className={`w-full text-left px-2.5 py-2 rounded-lg text-xs transition flex items-center justify-between group ${
                        isActive
                          ? "bg-[#1e2029] text-white font-medium border border-blue-500/30"
                          : "text-[#a1a1aa] hover:bg-[#1a1a1f] hover:text-[#e4e4e7]"
                      }`}
                    >
                      <div className="truncate pr-2">
                        <div className="truncate font-medium">{item.title}</div>
                        <div className="text-[10px] text-[#71717a] truncate font-mono mt-0.5">{item.timestamp}</div>
                      </div>
                      <span
                        className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold shrink-0 ${
                          item.score >= 80
                            ? "bg-blue-500/15 text-blue-400"
                            : item.score >= 65
                            ? "bg-sky-500/15 text-sky-400"
                            : item.score >= 50
                            ? "bg-amber-500/15 text-amber-400"
                            : "bg-rose-500/15 text-rose-400"
                        }`}
                      >
                        {item.score.toFixed(1)}
                      </span>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Footer: System Status & Developer Tools */}
        <div className="p-3 border-t border-[#222227] space-y-2 bg-[#101013]">
          <div className="flex items-center justify-between text-[11px] px-1 text-[#8e8e99]">
            <span className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  isDemoMode ? "bg-amber-400 animate-pulse" : "bg-emerald-400 animate-pulse"
                }`}
              />
              <span className="font-medium text-[#d4d4d8]">
                {isDemoMode ? "Offline Calibrated" : "NVIDIA NIM Engine"}
              </span>
            </span>
            <span className="text-[10px] font-mono text-[#52525c]">9-Dim v1</span>
          </div>

          <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px]">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="px-2 py-1.5 rounded-md bg-[#16161a] hover:bg-[#1f1f25] border border-[#24242a] text-[#a1a1aa] hover:text-white flex items-center justify-between transition"
            >
              <span>Swagger API</span>
              <ExternalLink className="w-3 h-3 text-[#52525c]" />
            </a>
            <a
              href="http://localhost:8000/metrics"
              target="_blank"
              rel="noreferrer"
              className="px-2 py-1.5 rounded-md bg-[#16161a] hover:bg-[#1f1f25] border border-[#24242a] text-[#a1a1aa] hover:text-white flex items-center justify-between transition"
            >
              <span>Prometheus</span>
              <Activity className="w-3 h-3 text-[#52525c]" />
            </a>
          </div>
        </div>
      </aside>

      {/* Backdrop for mobile drawer */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden"
        />
      )}

      {/* =========================================================================
          MAIN WORKSPACE AREA: Compact Top Bar + Split Central Workspace
         ========================================================================= */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden bg-[#0d0d0f]">
        {/* Compact Workspace Top Bar */}
        <header className="h-14 border-b border-[#222227] px-4 flex items-center justify-between bg-[#111114] shrink-0 z-20">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-1.5 rounded-md hover:bg-[#1f1f24] text-[#a1a1aa] hover:text-white transition"
              aria-label="Open sidebar"
            >
              <Menu className="w-4 h-4" />
            </button>

            {/* Breadcrumb title */}
            <div className="flex items-center gap-2">
              <Folder className="w-4 h-4 text-[#71717a]" />
              <div className="flex items-center gap-1.5 text-xs sm:text-sm">
                <span className="text-[#71717a] hidden sm:inline">Workspace /</span>
                <span className="font-semibold text-white tracking-tight truncate max-w-[200px] sm:max-w-md">
                  {sceneTitle}
                </span>
              </div>
            </div>

            {/* Status Pill */}
            {result ? (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/25">
                Score: {result.final_score.toFixed(1)} ({result.score_band})
              </span>
            ) : (
              <span className="hidden sm:inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-mono text-[#71717a] bg-[#18181c] border border-[#27272e]">
                Draft Excerpt
              </span>
            )}
          </div>

          {/* Top Bar Actions */}
          <div className="flex items-center gap-2">
            {result && (
              <button
                type="button"
                onClick={handleCopyReport}
                className="px-2.5 py-1.5 rounded-md bg-[#18181c] hover:bg-[#202026] text-[#d4d4d8] hover:text-white border border-[#27272e] text-xs font-medium flex items-center gap-1.5 transition"
                title="Copy markdown report"
              >
                {copiedReport ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Download className="w-3.5 h-3.5" />}
                <span className="hidden sm:inline">{copiedReport ? "Copied Report" : "Export Report"}</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => handleLoadPreset(PRESET_SCENES[0])}
              className="px-2.5 py-1.5 rounded-md bg-[#18181c] hover:bg-[#202026] text-[#d4d4d8] hover:text-white border border-[#27272e] text-xs font-medium transition"
            >
              Try sample
            </button>

            {inputText && (
              <button
                type="button"
                onClick={handleClear}
                className="px-2.5 py-1.5 rounded-md text-[#71717a] hover:text-white hover:bg-[#18181c] text-xs font-medium transition"
              >
                Clear
              </button>
            )}
          </div>
        </header>

        {/* Global Error Banner if any */}
        {errorMessage && (
          <div
            role="alert"
            className="px-4 py-2.5 bg-rose-950/60 border-b border-rose-800/40 text-rose-200 text-xs flex items-center justify-between"
          >
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-rose-400 hover:text-rose-100 font-bold px-1.5"
            >
              ×
            </button>
          </div>
        )}

        {/* Split Central Workspace */}
        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
          {/* =========================================================================
              LEFT SUB-PANE: Excerpt Editor (42% on desktop, stacks on mobile)
             ========================================================================= */}
          <section
            aria-label="Story Editor"
            className="lg:w-[42%] flex flex-col border-b lg:border-b-0 lg:border-r border-[#222227] bg-[#101013] shrink-0 h-1/2 lg:h-full overflow-hidden"
          >
            {/* Editor Sub-Header */}
            <div className="px-4 py-3 border-b border-[#222227] flex items-center justify-between shrink-0 bg-[#121216]">
              <div>
                <h2 className="text-xs font-semibold uppercase tracking-wider text-[#a1a1aa]">
                  Story Ending / Scene Excerpt
                </h2>
                <p className="text-[11px] text-[#71717a] mt-0.5">
                  Inspect stakes, ticking clocks, and unanswered questions.
                </p>
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={handlePasteClipboard}
                  className="px-2 py-1 text-[11px] font-medium text-[#d4d4d8] hover:text-white bg-[#1a1a1f] hover:bg-[#24242c] border border-[#2a2a34] rounded transition"
                  title="Paste from clipboard"
                >
                  Paste
                </button>
                {inputText && (
                  <button
                    type="button"
                    onClick={handleCopyInput}
                    className="px-2 py-1 text-[11px] font-medium text-[#d4d4d8] hover:text-white bg-[#1a1a1f] hover:bg-[#24242c] border border-[#2a2a34] rounded transition"
                  >
                    {copiedInput ? "Copied ✓" : "Copy"}
                  </button>
                )}
              </div>
            </div>

            {/* Textarea Workspace */}
            <div className="flex-1 p-4 flex flex-col relative min-h-0">
              <textarea
                ref={textareaRef}
                value={inputText}
                onChange={(e) => {
                  setInputText(e.target.value);
                  if (quoteMatchStatus) {
                    setQuoteMatchStatus(null);
                    setSelectedQuote(null);
                  }
                }}
                onKeyDown={handleKeyDown}
                placeholder="Paste the final 1–3 scenes or closing lines of your story or chapter here..."
                className="w-full flex-1 bg-[#0b0b0d] border border-[#222228] focus:border-blue-500/60 rounded-xl p-4 font-mono text-xs sm:text-sm text-[#e4e4e7] placeholder-[#4b4b55] focus:outline-none focus:ring-1 focus:ring-blue-500/30 leading-relaxed resize-none transition shadow-inner"
              />

              {pasteNotice && (
                <div className="absolute bottom-6 left-6 bg-[#1f1f25] text-white text-xs px-2.5 py-1.5 rounded-md border border-[#33333e] shadow-lg animate-fadeIn pointer-events-none">
                  {pasteNotice}
                </div>
              )}
            </div>

            {/* Editor Footer: Word Count, Shortcuts & Primary Action */}
            <div className="px-4 py-3 border-t border-[#222227] bg-[#121216] flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
              <div className="flex items-center gap-3 text-xs text-[#71717a] font-mono">
                <span>
                  {stats.words} {stats.words === 1 ? "word" : "words"}
                </span>
                <span>•</span>
                <span>{stats.chars} chars</span>
                <span className="hidden sm:inline text-[#52525c]">• ⌘/Ctrl+↵</span>
              </div>

              <button
                type="button"
                onClick={handleAnalyze}
                disabled={!inputText.trim() || analyzing}
                className={`py-2 px-4 rounded-lg font-medium text-xs sm:text-sm transition flex items-center justify-center gap-2 shadow-sm ${
                  !inputText.trim() || analyzing
                    ? "bg-[#1c1c22] text-[#555562] cursor-not-allowed border border-[#26262e]"
                    : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/30 active:scale-[0.99]"
                }`}
              >
                {analyzing ? (
                  <>
                    <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    <span>Evaluating ending tension...</span>
                  </>
                ) : (
                  <>
                    <span>Evaluate Ending Tension</span>
                    <CornerDownLeft className="w-3.5 h-3.5 text-blue-200" />
                  </>
                )}
              </button>
            </div>
          </section>

          {/* =========================================================================
              RIGHT SUB-PANE: Evaluation Results & Rewrite Lab (58% on desktop)
             ========================================================================= */}
          <section
            aria-label="Analysis Results"
            className="lg:w-[58%] flex flex-col bg-[#0d0d0f] flex-1 h-1/2 lg:h-full overflow-y-auto"
          >
            {result ? (
              <div className="p-4 sm:p-6 space-y-5 max-w-4xl mx-auto w-full">
                {/* 1. Score Overview Card (Codex charcoal surface) */}
                <div className="bg-[#151518] border border-[#24242a] rounded-xl p-5 shadow-sm">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#24242a]">
                    <div>
                      <span className="text-[11px] font-semibold tracking-wider uppercase text-[#858592] block">
                        Cliffhanger Strength Score
                      </span>
                      <div className="flex items-baseline gap-2.5 mt-1">
                        <span className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight font-mono">
                          {result.final_score.toFixed(1)}
                        </span>
                        <span className="text-[#71717a] text-sm font-mono font-medium">/ 100</span>
                      </div>
                    </div>

                    {bandMeta && (
                      <div className="sm:text-right">
                        <span className="text-[11px] font-medium text-[#858592] block mb-1">Calibrated Hook Rating</span>
                        <span
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border ${bandMeta.badgeClass}`}
                        >
                          <span aria-hidden="true">{bandMeta.symbol}</span>
                          <span>{bandMeta.label}</span>
                        </span>
                      </div>
                    )}
                  </div>

                  {bandMeta && (
                    <div className="mt-4 p-3 bg-[#0f0f12] rounded-lg border border-[#202026] text-xs text-[#a1a1aa] leading-relaxed flex items-start gap-2.5">
                      <Sparkles className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                      <div>
                        <p>{bandMeta.explanation}</p>
                        <p className="text-[10px] text-[#52525c] font-mono mt-1">
                          Deterministic arithmetic: Σ (weight_i × dimension_i) • Verified against verbatim excerpt
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* 2. Workspace View Tabs (Codex clean tab buttons) */}
                <div className="flex border-b border-[#24242a] space-x-1">
                  <button
                    type="button"
                    onClick={() => setActiveTab("dimensions")}
                    className={`px-3.5 py-2 text-xs font-medium border-b-2 transition flex items-center gap-1.5 ${
                      activeTab === "dimensions"
                        ? "border-blue-500 text-white font-semibold"
                        : "border-transparent text-[#8e8e99] hover:text-[#d4d4d8]"
                    }`}
                  >
                    <Sliders className="w-3.5 h-3.5" />
                    <span>9 Dimensions</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab("evidence")}
                    className={`px-3.5 py-2 text-xs font-medium border-b-2 transition flex items-center gap-1.5 ${
                      activeTab === "evidence"
                        ? "border-blue-500 text-white font-semibold"
                        : "border-transparent text-[#8e8e99] hover:text-[#d4d4d8]"
                    }`}
                  >
                    <BookOpen className="w-3.5 h-3.5" />
                    <span>Story Evidence & Devices</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab("rewrite")}
                    className={`px-3.5 py-2 text-xs font-medium border-b-2 transition flex items-center gap-1.5 ${
                      activeTab === "rewrite"
                        ? "border-blue-500 text-white font-semibold"
                        : "border-transparent text-[#8e8e99] hover:text-[#d4d4d8]"
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                    <span>Alternative Endings</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setActiveTab("report")}
                    className={`px-3.5 py-2 text-xs font-medium border-b-2 transition flex items-center gap-1.5 ${
                      activeTab === "report"
                        ? "border-blue-500 text-white font-semibold"
                        : "border-transparent text-[#8e8e99] hover:text-[#d4d4d8]"
                    }`}
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>Executive Report</span>
                  </button>
                </div>

                {/* Tab Pane 1: 9 Narrative Dimensions */}
                {activeTab === "dimensions" && (
                  <div className="space-y-3 animate-fadeIn">
                    <div className="flex items-center justify-between pb-1">
                      <div>
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-[#a1a1aa]">
                          Calibrated Dimension Ratings
                        </h3>
                        <p className="text-[11px] text-[#71717a]">
                          Each dimension is scored 0–100 with weighted contribution to final tension.
                        </p>
                      </div>
                      {lowestScoringDimension && (
                        <button
                          type="button"
                          onClick={() => {
                            setTargetDim(lowestScoringDimension.dimension_name);
                            setActiveTab("rewrite");
                          }}
                          className="text-[11px] text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition"
                        >
                          <span>Boost {DIMENSION_METADATA[lowestScoringDimension.dimension_name]?.label} →</span>
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-1 gap-2.5">
                      {result.dimension_breakdown.map((dim: DimensionScore) => {
                        const meta = DIMENSION_METADATA[dim.dimension_name] || {
                          label: dim.dimension_name.replace(/_/g, " "),
                          description: "Narrative dimension evaluation",
                          focusHint: "Improve narrative momentum.",
                        };

                        let barColor = "bg-blue-500";
                        let scoreColor = "text-blue-400";
                        if (dim.score >= 85) {
                          barColor = "bg-emerald-500";
                          scoreColor = "text-emerald-400";
                        } else if (dim.score < 65) {
                          barColor = "bg-amber-500";
                          scoreColor = "text-amber-400";
                        }

                        return (
                          <div
                            key={dim.dimension_name}
                            className="bg-[#151518] border border-[#24242a] hover:border-[#2f2f38] rounded-xl p-3.5 transition"
                          >
                            <div className="flex items-center justify-between text-xs">
                              <div className="flex items-center gap-2">
                                <span className="font-semibold text-white">{meta.label}</span>
                                <span className="text-[10px] text-[#71717a] font-mono">
                                  ({(dim.weight * 100).toFixed(0)}% weight)
                                </span>
                              </div>

                              <div className="flex items-center gap-1.5 font-mono text-xs">
                                <span className={`font-bold ${scoreColor}`}>{dim.score.toFixed(1)}</span>
                                <span className="text-[#52525c]">/ 100</span>
                              </div>
                            </div>

                            {/* Progress bar */}
                            <div className="w-full bg-[#1e1e24] rounded-full h-1.5 mt-2.5 overflow-hidden">
                              <div
                                className={`h-full rounded-full ${barColor} transition-all duration-500`}
                                style={{ width: `${Math.min(100, Math.max(0, dim.score))}%` }}
                              />
                            </div>

                            {/* Model Explanation */}
                            {dim.explanation && (
                              <p className="text-[11px] text-[#a1a1aa] mt-2 leading-relaxed font-sans">
                                {dim.explanation}
                              </p>
                            )}

                            {/* Dimension Craft Definition */}
                            <p className="text-[10px] text-[#52525c] mt-1 italic">{meta.description}</p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Tab Pane 2: Evidence & Narrative Devices */}
                {activeTab === "evidence" && (
                  <div className="space-y-5 animate-fadeIn">
                    {/* Story Evidence Quotes */}
                    <div className="bg-[#151518] border border-[#24242a] rounded-xl p-5 space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-[#24242a]">
                        <div>
                          <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
                            Verified Story Evidence Quotes
                          </h3>
                          <p className="text-[11px] text-[#71717a] mt-0.5">
                            Click any quote to highlight and locate it directly in the editor.
                          </p>
                        </div>
                        {quoteMatchStatus === "matched" && (
                          <span className="text-[11px] text-emerald-400 font-medium flex items-center gap-1 font-mono">
                            <Check className="w-3 h-3" /> Selected in editor
                          </span>
                        )}
                      </div>

                      <div className="space-y-2.5 pt-1">
                        {result.evidence_quotes && result.evidence_quotes.length > 0 ? (
                          result.evidence_quotes.map((quote: EvidenceQuote, idx: number) => {
                            const isSelected = selectedQuote === quote.quote;
                            return (
                              <div
                                key={idx}
                                onClick={() => handleQuoteClick(quote.quote)}
                                className={`p-3.5 rounded-lg border text-xs transition cursor-pointer ${
                                  isSelected
                                    ? "bg-blue-500/10 border-blue-500/40 shadow-sm"
                                    : "bg-[#111114] border-[#222228] hover:border-[#33333d]"
                                }`}
                              >
                                <div className="flex items-center justify-between text-[10px] text-[#71717a] mb-1.5">
                                  <span className="font-semibold uppercase font-mono text-[#a1a1aa]">
                                    {quote.location || "Cutoff Point"}
                                  </span>
                                  <span className="text-blue-400 hover:underline">Click to view in editor →</span>
                                </div>
                                <blockquote className="font-mono text-xs text-[#e4e4e7] border-l-2 border-blue-500 pl-3 py-0.5 leading-relaxed">
                                  "{quote.quote}"
                                </blockquote>
                              </div>
                            );
                          })
                        ) : (
                          <p className="text-xs text-[#71717a]">No verified quote citations extracted.</p>
                        )}
                      </div>
                    </div>

                    {/* Secondary Elements: Questions & Devices */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {/* Unresolved Questions */}
                      <div className="bg-[#151518] border border-[#24242a] rounded-xl p-4 space-y-2.5">
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-[#a1a1aa]">
                          Unresolved Hook Questions
                        </h4>
                        <p className="text-[11px] text-[#71717a]">Core curiosities compelling the next page:</p>
                        <ul className="text-xs text-[#d4d4d8] space-y-1.5 list-disc pl-4 leading-relaxed">
                          {result.open_questions && result.open_questions.length > 0 ? (
                            result.open_questions.map((q: string, idx: number) => <li key={idx}>{q}</li>)
                          ) : (
                            <li className="text-[#71717a] italic list-none -ml-4">No major open questions flagged.</li>
                          )}
                        </ul>
                      </div>

                      {/* Detected Cliffhanger Taxonomy Tags */}
                      <div className="bg-[#151518] border border-[#24242a] rounded-xl p-4 space-y-2.5">
                        <h4 className="text-xs font-semibold uppercase tracking-wider text-[#a1a1aa]">
                          Detected Dramatic Devices
                        </h4>
                        <p className="text-[11px] text-[#71717a]">Mechanisms found in the cutoff beat:</p>
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {result.taxonomy_classifications && result.taxonomy_classifications.length > 0 ? (
                            result.taxonomy_classifications.map((item: TaxonomyTag) => (
                              <span
                                key={item.type}
                                title={item.rationale}
                                className="px-2.5 py-1 rounded-md text-[11px] font-mono bg-[#1c1c24] text-blue-300 border border-blue-500/20"
                              >
                                {TAXONOMY_LABELS[item.type] || item.type} ({Math.round(item.confidence * 100)}%)
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-[#71717a] italic">None detected.</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Tab Pane 3: Alternative Endings (Rewrite Lab) */}
                {activeTab === "rewrite" && (
                  <div className="bg-[#151518] border border-[#24242a] rounded-xl p-5 space-y-5 animate-fadeIn">
                    <div className="border-b border-[#24242a] pb-3">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
                          Synthesize Alternative Ending
                        </h3>
                        {lowestScoringDimension && (
                          <span className="text-[11px] px-2 py-0.5 rounded font-mono bg-amber-500/10 text-amber-300 border border-amber-500/20">
                            Recommended: {DIMENSION_METADATA[lowestScoringDimension.dimension_name]?.label} (
                            {lowestScoringDimension.score.toFixed(0)}/100)
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-[#71717a] mt-1">
                        Dials up tension for a targeted dimension while strictly preserving established scene facts and voice.
                      </p>
                    </div>

                    {/* Selector and Trigger */}
                    <div className="space-y-3">
                      <label htmlFor="dim-select" className="text-xs font-medium text-[#d4d4d8] block">
                        Target Dimension to Heighten:
                      </label>

                      <div className="flex flex-col sm:flex-row gap-2.5">
                        <select
                          id="dim-select"
                          value={targetDim}
                          onChange={(e) => setTargetDim(e.target.value)}
                          className="bg-[#0f0f12] border border-[#282832] text-xs sm:text-sm text-[#e4e4e7] rounded-lg px-3.5 py-2.5 flex-1 focus:outline-none focus:border-blue-500 font-sans"
                        >
                          {result.dimension_breakdown.map((d: DimensionScore) => {
                            const meta = DIMENSION_METADATA[d.dimension_name];
                            return (
                              <option key={d.dimension_name} value={d.dimension_name}>
                                {meta?.label || d.dimension_name} (Current: {d.score.toFixed(0)}/100)
                              </option>
                            );
                          })}
                        </select>

                        <button
                          type="button"
                          onClick={handleRewrite}
                          disabled={rewriting}
                          className={`px-4 py-2.5 rounded-lg font-medium text-xs sm:text-sm transition flex items-center justify-center gap-2 shadow-sm ${
                            rewriting
                              ? "bg-[#1f1f26] text-[#71717a] cursor-not-allowed"
                              : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-900/20"
                          }`}
                        >
                          {rewriting ? (
                            <>
                              <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                              </svg>
                              <span>Drafting revision...</span>
                            </>
                          ) : (
                            <>
                              <Sparkles className="w-3.5 h-3.5" />
                              <span>Draft Alternative</span>
                            </>
                          )}
                        </button>
                      </div>

                      {rewriteError && <p className="text-xs text-rose-400">{rewriteError}</p>}
                    </div>

                    {/* Empty State when no alternative has been drafted for this analysis */}
                    {!rewriteResult && !rewriting && (
                      <div className="p-6 text-center rounded-lg border border-dashed border-[#26262e] text-[#6b6b7a] space-y-2">
                        <Sparkles className="w-6 h-6 mx-auto text-blue-400 opacity-60" />
                        <div className="text-xs font-medium text-[#d4d4d8]">No alternative ending generated yet</div>
                        <div className="text-[11px] text-[#71717a] max-w-sm mx-auto">
                          Select a target dimension above and click &quot;Draft Alternative&quot; to synthesize an ending tailored to this analysis.
                        </div>
                      </div>
                    )}

                    {/* Revision Output Comparison */}
                    {rewriteResult && (
                      <div className="pt-3 border-t border-[#24242a] space-y-4 animate-fadeIn">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold uppercase tracking-wider text-white">
                            Revision Comparison
                          </span>
                          {rewriteResult.is_consistent && (
                            <span className="text-[11px] text-emerald-400 font-medium font-mono flex items-center gap-1">
                              <Check className="w-3 h-3" /> Narrative Continuity Verified
                            </span>
                          )}
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                          {/* Original */}
                          <div className="bg-[#101013] border border-[#222228] rounded-lg p-3.5 space-y-2">
                            <div className="flex items-center justify-between text-[11px] pb-1 border-b border-[#1f1f25]">
                              <span className="font-semibold text-[#8e8e99] uppercase tracking-wider">
                                Current Excerpt
                              </span>
                              <span className="font-mono text-[#71717a]">
                                Score: {rewriteResult.original_score.toFixed(1)}
                              </span>
                            </div>
                            <p className="text-xs text-[#a1a1aa] font-mono leading-relaxed line-clamp-6">
                              {inputText}
                            </p>
                          </div>

                          {/* Revised */}
                          <div className="bg-[#12141a] border border-blue-500/30 rounded-lg p-3.5 space-y-2.5 shadow-sm">
                            <div className="flex items-center justify-between text-[11px] pb-1 border-b border-blue-500/20">
                              <span className="font-semibold text-blue-400 uppercase tracking-wider">
                                Suggested Alternative
                              </span>
                              <div className="flex items-center gap-1.5 font-mono text-xs">
                                <span className="text-white font-bold">{rewriteResult.predicted_score.toFixed(1)}</span>
                                <span className="text-emerald-400 font-semibold">
                                  (+{rewriteResult.score_delta > 0 ? rewriteResult.score_delta.toFixed(1) : "0.0"})
                                </span>
                              </div>
                            </div>

                            <p className="text-xs text-[#e4e4e7] font-mono leading-relaxed">
                              {rewriteResult.content}
                            </p>

                            {rewriteResult.validation_critique && (
                              <p className="text-[10px] text-[#71717a] italic pt-1 border-t border-[#1e2029]">
                                Continuity Audit: {rewriteResult.validation_critique}
                              </p>
                            )}

                            <div className="flex items-center justify-end gap-2 pt-2">
                              <button
                                type="button"
                                onClick={handleCopyRewrite}
                                className="px-2.5 py-1 text-xs text-[#d4d4d8] hover:text-white bg-[#1a1a1f] hover:bg-[#25252e] border border-[#2b2b35] rounded transition"
                              >
                                {copiedRewrite ? "Copied ✓" : "Copy Revision"}
                              </button>
                              <button
                                type="button"
                                onClick={handleApplyRewriteToInput}
                                className="px-2.5 py-1 text-xs text-white bg-blue-600 hover:bg-blue-500 rounded transition font-medium"
                              >
                                Use in Editor
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Tab Pane 4: Executive Report */}
                {activeTab === "report" && (
                  <div className="bg-[#151518] border border-[#24242a] rounded-xl p-5 space-y-4 animate-fadeIn">
                    <div className="flex items-center justify-between pb-3 border-b border-[#24242a]">
                      <div>
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-white">
                          Evaluation Executive Summary
                        </h3>
                        <p className="text-[11px] text-[#71717a]">
                          Exportable markdown report for story editors and writing rooms.
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={handleCopyReport}
                        className="px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium flex items-center gap-1.5 transition"
                      >
                        {copiedReport ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                        <span>{copiedReport ? "Copied Report" : "Copy Markdown"}</span>
                      </button>
                    </div>

                    <div className="bg-[#0b0b0d] p-4 rounded-lg border border-[#222228] font-mono text-xs text-[#a1a1aa] whitespace-pre-wrap leading-relaxed select-all">
                      {`# Cliffhanger Strength Evaluation Report
Scene: ${sceneTitle}
Overall Score: ${result.final_score.toFixed(1)} / 100 (${result.score_band})
Engine: ${result.model_name}

## 9 Dimension Breakdown:
${result.dimension_breakdown
  .map(
    (d) =>
      `- ${DIMENSION_METADATA[d.dimension_name]?.label || d.dimension_name}: ${d.score.toFixed(1)}/100 (Weight: ${(
        d.weight * 100
      ).toFixed(0)}%) - ${d.explanation}`
  )
  .join("\n")}

## Unresolved Questions:
${result.open_questions.map((q) => `- ${q}`).join("\n")}

## Story Ending Excerpt:
${inputText}`}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* =========================================================================
                 EMPTY STATE: Clean Codex-inspired Card with 3-Step Guidance
                 ========================================================================= */
              <div className="p-6 sm:p-10 my-auto flex flex-col items-center justify-center max-w-xl mx-auto w-full text-center">
                <div className="w-12 h-12 rounded-xl bg-[#18181d] border border-[#292933] text-blue-400 flex items-center justify-center text-lg mb-4 shadow-sm">
                  <Activity className="w-6 h-6 text-blue-400" />
                </div>

                <h2 className="text-lg font-bold text-white tracking-tight">Ready to evaluate your cliffhanger</h2>
                <p className="text-xs sm:text-sm text-[#8e8e99] mt-1.5 max-w-md leading-relaxed">
                  Test how effectively your chapter cutoff or scene climax builds suspense and drives reader engagement across
                  9 calibrated narrative dimensions.
                </p>

                {/* 3 Step Guidance Cards matching the user's second image */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full text-left my-6">
                  <div className="p-3.5 bg-[#141417] border border-[#24242a] rounded-xl space-y-1">
                    <span className="text-xs font-mono font-bold text-blue-400">01</span>
                    <h3 className="text-xs font-semibold text-white">Paste Ending</h3>
                    <p className="text-[11px] text-[#71717a] leading-normal">
                      Input the final scenes or dialogue right before your cut.
                    </p>
                  </div>

                  <div className="p-3.5 bg-[#141417] border border-[#24242a] rounded-xl space-y-1">
                    <span className="text-xs font-mono font-bold text-blue-400">02</span>
                    <h3 className="text-xs font-semibold text-white">Evaluate Tension</h3>
                    <p className="text-[11px] text-[#71717a] leading-normal">
                      Receive an overall score, score band, and 9-dimension rating.
                    </p>
                  </div>

                  <div className="p-3.5 bg-[#141417] border border-[#24242a] rounded-xl space-y-1">
                    <span className="text-xs font-mono font-bold text-blue-400">03</span>
                    <h3 className="text-xs font-semibold text-white">Test Rewrites</h3>
                    <p className="text-[11px] text-[#71717a] leading-normal">
                      Synthesize targeted endings to sharpen weak dimensions.
                    </p>
                  </div>
                </div>

                {/* Action button */}
                <div className="space-y-3">
                  <button
                    type="button"
                    onClick={() => handleLoadPreset(PRESET_SCENES[0])}
                    className="px-5 py-2.5 rounded-lg font-medium text-xs sm:text-sm bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-900/30 transition flex items-center gap-2 mx-auto active:scale-[0.99]"
                  >
                    <span>Load Sample Scene to Begin</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>

                  <div className="flex flex-wrap items-center justify-center gap-1.5 pt-1">
                    <span className="text-[11px] text-[#52525c]">Or quick test:</span>
                    {PRESET_SCENES.slice(1).map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => handleLoadPreset(p)}
                        className="text-[11px] px-2 py-0.5 rounded bg-[#18181c] hover:bg-[#222228] text-[#a1a1aa] hover:text-white border border-[#26262e] transition font-mono"
                      >
                        {p.title}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
