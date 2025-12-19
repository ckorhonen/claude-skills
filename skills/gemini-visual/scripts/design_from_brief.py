#!/usr/bin/env python3
"""
Design from Brief - Generate frontend designs and code from text descriptions.

Use Gemini 3 to get design advice, generate UI code, and iterate on ideas
from text briefs without needing visual input.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Exit codes
EXIT_SUCCESS = 0
EXIT_MISSING_API_KEY = 1
EXIT_INVALID_ARGS = 2
EXIT_API_ERROR = 3
EXIT_SAVE_ERROR = 4

# Configuration
DEFAULT_MODEL = "gemini-3-pro-preview"
VALID_MODES = ["design", "code", "component", "review", "brainstorm"]
VALID_FRAMEWORKS = ["tailwind", "css", "bootstrap", "react", "vue", "svelte", "vanilla"]
VALID_FORMATS = ["text", "json", "markdown"]

# Mode-specific system prompts
MODE_PROMPTS = {
    "design": """You are an expert UI/UX designer helping to design frontend interfaces.

When given a design brief, provide:

1. **Design Concept**
   - Overall visual direction and style
   - Color palette recommendations (with HEX codes)
   - Typography suggestions (fonts, sizes, hierarchy)
   - Layout approach (grid, spacing)

2. **Component Breakdown**
   - List of UI components needed
   - Component hierarchy and relationships
   - State variations (hover, active, disabled, etc.)

3. **User Experience Considerations**
   - Information hierarchy
   - User flow suggestions
   - Accessibility recommendations
   - Responsive design strategy

4. **Visual References**
   - Describe the aesthetic in detail
   - Suggest similar design patterns or styles
   - Mood/atmosphere description

Provide specific, actionable design decisions that can be implemented.""",

    "code": """You are an expert frontend developer generating production-ready code.

When given a design brief or description, generate:

1. **Complete, working code** using the specified framework
2. **Semantic HTML5** structure
3. **Responsive design** with mobile-first approach
4. **Accessibility features** (ARIA labels, semantic elements, focus states)
5. **Clean, well-commented code** following best practices

Output format:
- Provide complete code blocks that can be copied and used directly
- Include any necessary CSS/styles
- Add comments explaining key decisions
- Suggest any additional dependencies needed

Focus on pixel-perfect, production-quality code.""",

    "component": """You are an expert component designer creating reusable UI components.

When given a component description, provide:

1. **Component Specification**
   - Props/parameters and their types
   - State management approach
   - Events/callbacks
   - Variants and sizes

2. **Complete Component Code**
   - Full implementation in the specified framework
   - TypeScript types (if applicable)
   - CSS/styling (scoped or module)
   - Default props and prop validation

3. **Usage Examples**
   - Basic usage
   - With different props
   - In context of a larger UI

4. **Testing Considerations**
   - Key test cases
   - Accessibility testing points
   - Edge cases to handle

Create production-ready, reusable components.""",

    "review": """You are an expert frontend architect reviewing designs and code.

When given a description or code to review, provide:

1. **Strengths**
   - What works well
   - Good patterns being used
   - Positive UX decisions

2. **Issues & Concerns**
   - Potential problems
   - Accessibility issues
   - Performance concerns
   - Security considerations

3. **Recommendations**
   - Specific improvements with code examples
   - Alternative approaches
   - Best practices to apply

4. **Priority Actions**
   - Must-fix issues
   - Should-fix improvements
   - Nice-to-have enhancements

Be constructive and provide actionable feedback with examples.""",

    "brainstorm": """You are a creative UI/UX consultant brainstorming design ideas.

When given a project brief, provide:

1. **Multiple Design Directions** (3-5 options)
   - Each with a distinct visual style
   - Pros and cons of each approach
   - Target audience fit

2. **Creative Ideas**
   - Innovative interaction patterns
   - Unique visual treatments
   - Micro-interactions and animations
   - Delight factors

3. **Inspiration Sources**
   - Similar successful products
   - Design trends to consider
   - Patterns that work well for this use case

4. **Technical Feasibility**
   - Implementation complexity for each idea
   - Framework/tool recommendations
   - Performance considerations

Be creative and think outside the box while remaining practical."""
}

# Framework-specific additions
FRAMEWORK_ADDITIONS = {
    "tailwind": "\n\nUse Tailwind CSS utility classes for all styling. Include any custom theme extensions needed.",
    "css": "\n\nUse modern CSS with custom properties (variables) and BEM naming convention.",
    "bootstrap": "\n\nUse Bootstrap 5 components and utilities. Only add custom CSS when Bootstrap doesn't cover it.",
    "react": "\n\nGenerate React functional components with hooks. Use TypeScript for type safety.",
    "vue": "\n\nGenerate Vue 3 components using Composition API with <script setup>. Include TypeScript.",
    "svelte": "\n\nGenerate Svelte components with reactive declarations. Keep logic clean and simple.",
    "vanilla": "\n\nUse plain HTML, CSS, and JavaScript. No frameworks or libraries.",
}


def get_api_key() -> str:
    """Get the Gemini API key from environment variable."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        print("\nTo get an API key:", file=sys.stderr)
        print("1. Go to https://aistudio.google.com/apikey", file=sys.stderr)
        print("2. Create or select a project", file=sys.stderr)
        print("3. Generate an API key", file=sys.stderr)
        print("\nThen set the environment variable:", file=sys.stderr)
        print("  export GEMINI_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(EXIT_MISSING_API_KEY)
    return api_key


def read_brief_file(file_path: str) -> str:
    """Read a brief from a file."""
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Brief file not found: {path}", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)
    return path.read_text()


def generate_from_brief(
    brief: str,
    mode: str = "code",
    framework: str = "tailwind",
    output_format: str = "text",
    context: Optional[str] = None,
    verbose: bool = False,
) -> str:
    """Generate design/code from a text brief using Gemini 3."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.", file=sys.stderr)
        print("Install it with: pip install google-genai", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    api_key = get_api_key()

    if verbose:
        print(f"[*] Mode: {mode}")
        print(f"[*] Framework: {framework}")
        print(f"[*] Brief length: {len(brief)} characters")

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Build system prompt
    system_prompt = MODE_PROMPTS[mode]

    # Add framework-specific instructions for code modes
    if mode in ["code", "component"] and framework:
        system_prompt += FRAMEWORK_ADDITIONS.get(framework, "")

    # Add output format instruction
    if output_format == "json":
        system_prompt += "\n\nFormat your response as a valid JSON object with appropriate keys."
    elif output_format == "markdown":
        system_prompt += "\n\nFormat your response using Markdown with headers, code blocks, and lists."

    # Build the full prompt
    full_prompt = f"{system_prompt}\n\n---\n\n**Brief:**\n{brief}"

    # Add context if provided
    if context:
        full_prompt += f"\n\n**Additional Context:**\n{context}"

    if verbose:
        print(f"[*] Sending request to Gemini 3...")

    # Configure generation
    config = types.GenerateContentConfig(
        temperature=0.8 if mode == "brainstorm" else 0.7,
    )

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=full_prompt,
            config=config,
        )
    except Exception as e:
        error_msg = str(e)
        if "rate" in error_msg.lower() or "quota" in error_msg.lower():
            print("Error: Rate limit exceeded. Please wait and try again.", file=sys.stderr)
        else:
            print(f"Error: API request failed: {error_msg}", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    if verbose:
        print(f"[*] Response received")

    # Extract response
    if not response.candidates:
        print("Error: No response from API.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)

    try:
        return response.text
    except Exception:
        print("Error: Could not extract text from response.", file=sys.stderr)
        sys.exit(EXIT_API_ERROR)


def interactive_session(
    mode: str = "code",
    framework: str = "tailwind",
    verbose: bool = False,
) -> None:
    """Run an interactive design session with multi-turn conversation."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("Error: google-genai package not installed.", file=sys.stderr)
        print("Install it with: pip install google-genai", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)

    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    # Build system prompt
    system_prompt = MODE_PROMPTS[mode]
    if mode in ["code", "component"] and framework:
        system_prompt += FRAMEWORK_ADDITIONS.get(framework, "")

    print(f"Interactive Design Session ({mode} mode, {framework})")
    print("=" * 50)
    print("Type your design brief or questions. Commands:")
    print("  /mode <mode>     - Change mode (design, code, component, review, brainstorm)")
    print("  /framework <fw>  - Change framework")
    print("  /save <file>     - Save last response to file")
    print("  /clear           - Clear conversation history")
    print("  /quit            - Exit session")
    print("=" * 50)
    print()

    conversation_history = []
    last_response = ""

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()

            if cmd == "/quit":
                print("Goodbye!")
                break
            elif cmd == "/clear":
                conversation_history = []
                print("Conversation cleared.")
                continue
            elif cmd == "/mode" and len(parts) > 1:
                new_mode = parts[1].lower()
                if new_mode in VALID_MODES:
                    mode = new_mode
                    system_prompt = MODE_PROMPTS[mode]
                    if mode in ["code", "component"]:
                        system_prompt += FRAMEWORK_ADDITIONS.get(framework, "")
                    print(f"Mode changed to: {mode}")
                else:
                    print(f"Invalid mode. Choose from: {', '.join(VALID_MODES)}")
                continue
            elif cmd == "/framework" and len(parts) > 1:
                new_fw = parts[1].lower()
                if new_fw in VALID_FRAMEWORKS:
                    framework = new_fw
                    if mode in ["code", "component"]:
                        system_prompt = MODE_PROMPTS[mode] + FRAMEWORK_ADDITIONS.get(framework, "")
                    print(f"Framework changed to: {framework}")
                else:
                    print(f"Invalid framework. Choose from: {', '.join(VALID_FRAMEWORKS)}")
                continue
            elif cmd == "/save" and len(parts) > 1:
                save_path = Path(parts[1])
                try:
                    save_path.write_text(last_response)
                    print(f"Saved to: {save_path}")
                except Exception as e:
                    print(f"Error saving: {e}")
                continue
            else:
                print("Unknown command. Type /quit to exit.")
                continue

        # Add user message to history
        conversation_history.append({
            "role": "user",
            "parts": [user_input]
        })

        # Build full conversation with system prompt
        contents = [system_prompt] + [
            {"role": msg["role"], "parts": msg["parts"]}
            for msg in conversation_history
        ]

        try:
            response = client.models.generate_content(
                model=DEFAULT_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(temperature=0.7),
            )

            if response.candidates:
                last_response = response.text
                conversation_history.append({
                    "role": "model",
                    "parts": [last_response]
                })
                print(f"\nGemini:\n{last_response}\n")
            else:
                print("No response received.")
        except Exception as e:
            print(f"Error: {e}")


def save_output(content: str, output_path: str, verbose: bool = False) -> None:
    """Save output to file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_text(content)
        if verbose:
            print(f"[*] Output saved to: {path}")
    except Exception as e:
        print(f"Error: Failed to save output: {e}", file=sys.stderr)
        sys.exit(EXIT_SAVE_ERROR)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate frontend designs and code from text briefs using Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate code from a brief
  %(prog)s -p "Create a pricing table with 3 tiers" -m code -fw tailwind

  # Get design advice
  %(prog)s -p "Design a modern SaaS landing page" -m design

  # Generate a React component
  %(prog)s -p "A toggle switch with smooth animation" -m component -fw react

  # Review a design idea
  %(prog)s -p "Is a hamburger menu good for desktop?" -m review

  # Brainstorm ideas
  %(prog)s -p "Ideas for a fitness app dashboard" -m brainstorm

  # Read brief from file
  %(prog)s -b brief.txt -m code -fw vue

  # Interactive session
  %(prog)s --interactive -m code -fw tailwind

Modes:
  design      Get design guidance, colors, typography, layout
  code        Generate complete frontend code
  component   Design and code reusable components
  review      Get feedback on designs or code
  brainstorm  Generate creative ideas and directions

Frameworks:
  tailwind    Tailwind CSS
  css         Custom CSS
  bootstrap   Bootstrap 5
  react       React with TypeScript
  vue         Vue 3 Composition API
  svelte      Svelte
  vanilla     Plain HTML/CSS/JS

Environment:
  GEMINI_API_KEY  Required. Get from https://aistudio.google.com/apikey
        """
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-p", "--prompt",
        help="Design brief or prompt text"
    )
    input_group.add_argument(
        "-b", "--brief-file",
        help="Read brief from a file"
    )
    input_group.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive design session"
    )

    parser.add_argument(
        "-m", "--mode",
        default="code",
        choices=VALID_MODES,
        help="Generation mode (default: code)"
    )
    parser.add_argument(
        "-fw", "--framework",
        default="tailwind",
        choices=VALID_FRAMEWORKS,
        help="CSS/JS framework for code generation (default: tailwind)"
    )
    parser.add_argument(
        "-c", "--context",
        help="Additional context (existing code, constraints, etc.)"
    )
    parser.add_argument(
        "-f", "--format",
        default="text",
        choices=VALID_FORMATS,
        dest="output_format",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save output to file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    # Handle interactive mode
    if args.interactive:
        interactive_session(
            mode=args.mode,
            framework=args.framework,
            verbose=args.verbose,
        )
        return EXIT_SUCCESS

    # Require prompt or brief file for non-interactive mode
    if not args.prompt and not args.brief_file:
        parser.error("One of -p/--prompt, -b/--brief-file, or --interactive is required")

    # Get brief text
    if args.brief_file:
        brief = read_brief_file(args.brief_file)
    else:
        brief = args.prompt

    # Generate response
    result = generate_from_brief(
        brief=brief,
        mode=args.mode,
        framework=args.framework,
        output_format=args.output_format,
        context=args.context,
        verbose=args.verbose,
    )

    # Save or print output
    if args.output:
        save_output(result, args.output, args.verbose)
        print(f"Output saved to: {args.output}")
    else:
        print(result)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
