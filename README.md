# VoteWise — Voting Reality Scanner

*"A system that tells you whether you can actually vote — and why."*

## Problem Statement

Many citizens believe they are eligible to vote, but in reality:
- They are not registered.
- They miss critical deadlines.
- They don't understand the timelines required for voter processing.

This disconnect leads to lost voting opportunities and low civic participation.

## Solution Overview

VoteWise solves this problem by:
- Analyzing user readiness deterministically.
- Simulating real-world timelines.
- Showing whether voting is actually possible given current constraints.
- Providing clear reasoning and immediate action steps.

## Key Features

- **Voting Reality Scanner**: Instantly determines if you can actually vote.
- **Timeline Simulation**: A visual representation of time logic (e.g., today vs. election day vs. registration completion).
- **Decision Impact Engine**: Contrasts the consequence of acting today versus delaying.
- **Dynamic Personalization**: Insights tailored directly to the user's specific timeline gaps.
- **Area Insight**: Displays local context including MLA, MP, and Party in Power (using a demo dataset).
- **Reality Gap Insight**: Connects the user's lack of readiness directly to their lack of civic participation.

## How It Works

1. **User Selects**: 
   - State
   - District
   - Age
   - Registration status
2. **System Calculates**:
   - The required time for registration to complete.
   - The time left before the election.
3. **System Generates**:
   - A final verdict (e.g., "Ready Voter" or "Likely Miss").
   - A visual timeline simulation highlighting any mismatch.
   - Impact scenarios based on delayed action.
   - Personalized reasoning breaking down the exact timeline.

## Unique Value Proposition

Unlike traditional tools that simply provide information, VoteWise provides:
- **A decision** (not just data)
- **A simulation** (not just an explanation)
- **A consequence** (not just a suggestion)

## Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML, CSS, JavaScript
- **Data**: Local static dataset
- **Core**: Logic-driven simulation system

## System Design (High-Level)

- **Input Layer**: Collects user state, location, and registration status.
- **Logic Engine**: Applies strict rules and timeline calculations to determine readiness.
- **Simulation Layer**: Translates logic into visual timelines and outcome scenarios.
- **UI Layer**: A clean, card-based visual dashboard presenting the verdict and insights.

## Tool Usage (Mandatory for Prompt Wars)

**Google Antigravity:**
- Used to rapidly build and iterate the UI and core logic using prompt-based development.

**Gemini:**
- Used optionally for refining and improving text explanations, ensuring clarity without generating factual data.

**Why AI was used:**
- Ensured extremely fast prototyping and iteration.
- Maintained strict control over the accuracy of the deterministic logic.

**Division of Labor:**
- **What AI handled**: UI generation, styling, and text refinement.
- **What human designed**: Core logic architecture, the decision system rules, and the fundamental product idea.

## Future Scope

- Integration with real election APIs.
- Live MLA/MP data pulling.
- Real-time election timelines based on official schedules.
- User login, progress tracking, and secure state management.
- Push notifications and reminders for deadlines.

## Conclusion

VoteWise is designed to bridge the gap between intention and action in voting, ensuring users not only understand the process but act in time to make their voice heard.
