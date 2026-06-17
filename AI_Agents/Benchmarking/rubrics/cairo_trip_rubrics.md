graders:
  - type: llm_rubric
    rubric: Benchmarking/rubrics/cairo_trip_rubrics.md
    assertions:
      - "Travel Plan correctly strictly follows the schema."
      - "Accommodation suggestions are relevant to the city and user preferences."
      - "Activities are varied and match the user's interests (history, culture, food)."
      - "Budget constraints are respected throughout the itinerary."
      - "Transportation methods are practical and efficient for the region."
      - "The plan is coherent and easy to follow."
  - type: llm_rubric
    rubric: Benchmarking/judge.py
    assertions:
      - "Travel plan is spacially reasonable"
tracked_metrics:
  - type: transcript
    metrics:
      - n_turns
      - n_toolcalls
      - n_total_tokens
  - type: latency
    metrics:
      - time_to_first_token
      - output_tokens_per_sec
      - time_to_last_token
