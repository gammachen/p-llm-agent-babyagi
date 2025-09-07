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
'''

from print import slow_print_file

slow_print_file(file_path="tmp.md")