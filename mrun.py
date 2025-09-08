'''


SYNC kwargs[caching]: False; litellm.cache: None; kwargs.get('cache')['no-cache']: False

Provider List: https://docs.litellm.ai/docs/providers

Error executing function chat_with_functions: litellm.BadRequestError: LLM Provider NOT provided. Pass in the LLM provider you are trying to call. You passed model=gpt-3.5-turbo
 Pass model as E.g. For 'Huggingface' inference endpoints pass in `completion(model='huggingface/starcoder',..)` Learn more: https://docs.litellm.ai/docs/providers
Traceback (most recent call last):
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-babyagi/babyagi-agent-native/babyagi-main/babyagi/api/__init__.py", line 71, in execute_function
    result = g.functionz.executor.execute(function_name, **params)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/shhaofu/Code/cursor-projects/p-llm-agent-babyagi/babyagi-agent-native/babyagi-main/babyagi/functionz/core/execution.py", line 217, in execute
    output = func(*bound_args.args, **bound_args.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<string>", line 97, in chat_with_functions
  File "/opt/anaconda3/envs/babyagi/lib/python3.11/site-packages/litellm/utils.py", line 1342, in wrapper
    raise e
  File "/opt/anaconda3/envs/babyagi/lib/python3.11/site-packages/litellm/utils.py", line 1217, in wrapper
    result = original_function(*args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/babyagi/lib/python3.11/site-packages/litellm/main.py", line 3586, in completion
    raise exception_type(
  File "/opt/anaconda3/envs/babyagi/lib/python3.11/site-packages/litellm/main.py", line 1109, in completion
    model, custom_llm_provider, dynamic_api_key, api_base = get_llm_provider(
                                                            ^^^^^^^^^^^^^^^^^
  File "/opt/anaconda3/envs/babyagi/lib/python3.11/site-packages/litellm/litellm_core_utils/get_llm_provider_logic.py", line 404, in get_llm_provider
    raise e
  File "/opt/anaconda3/envs/babyagi/lib/python3.11/site-packages/litellm/litellm_core_utils/get_llm_provider_logic.py", line 381, in get_llm_provider
    raise litellm.exceptions.BadRequestError(  # type: ignore
litellm.exceptions.BadRequestError: litellm.BadRequestError: LLM Provider NOT provided. Pass in the LLM provider you are trying to call. You passed model=gpt-3.5-turbo
 Pass model as E.g. For 'Huggingface' inference endpoints pass in `completion(model='huggingface/starcoder',..)` Learn more: https://docs.litellm.ai/docs/providers

{
	"id": "chatcmpl-991",
	"choices": [{
		"finish_reason": "tool_calls",
		"index": 0,
		"logprobs": null,
		"message": {
			"content": "为了提供您的请求，我将调用相关的API来查询所需信息。\n\n首先是对张三的学生档案的查询：\n",
			"refusal": null,
			"role": "assistant",
			"annotations": null,
			"audio": null,
			"function_call": null,
			"tool_calls": [{
				"id": "call_qcsnph9z",
				"function": {
					"arguments": "{\"student_name\":\"张三\"}",
					"name": "get_student_info"
				},
				"type": "function",
				"index": 0
			}, {
				"id": "call_fsbrn8u0",
				"function": {
					"arguments": "{\"student_id\":\"STU2024001\"}",
					"name": "get_student_latest_grade_by_id"
				},
				"type": "function",
				"index": 1
			}, {
				"id": "call_4b5oumxh",
				"function": {
					"arguments": "{\"query_type\":\"current\",\"student_id\":\"STU2024001\"}",
					"name": "get_library_records"
				},
				"type": "function",
				"index": 2
			}, {
				"id": "call_tfig18tm",
				"function": {
					"arguments": "{}",
					"name": "get_sports_activities"
				},
				"type": "function",
				"index": 3
			}]
		}
	}],
	"created": 1757262094,
	"model": "gpt-3.5-turbo",
	"object": "chat.completion",
	"service_tier": null,
	"system_fingerprint": "fp_ollama",
	"usage": {
		"completion_tokens": 223,
		"prompt_tokens": 1661,
		"total_tokens": 1884,
		"completion_tokens_details": null,
		"prompt_tokens_details": null
	}
}

'''

from print import slow_print_file

slow_print_file(file_path="tmp.md")