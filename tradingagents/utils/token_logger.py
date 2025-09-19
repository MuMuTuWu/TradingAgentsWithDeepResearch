"""Token使用情况记录工具"""

def print_token_usage(response, context_name="LLM调用"):
    """
    打印LLM响应中的token使用信息
    
    Args:
        response: LLM响应对象
        context_name: 调用上下文名称，用于标识是哪个组件的调用
    """
    try:
        # 尝试从response_metadata获取usage信息
        usage_info = None
        
        # 检查response_metadata中的usage
        if hasattr(response, 'response_metadata') and response.response_metadata:
            usage_info = response.response_metadata.get('usage')
        
        # 如果没有在response_metadata中找到，检查usage_metadata
        if not usage_info and hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage_info = response.usage_metadata
            
        # 如果还没找到，检查additional_kwargs
        if not usage_info and hasattr(response, 'additional_kwargs') and response.additional_kwargs:
            usage_info = response.additional_kwargs.get('usage')
        
        if usage_info:
            print(f"\n=== {context_name} Token使用情况 ===")
            
            # 输入tokens
            input_tokens = usage_info.get('input_tokens') or usage_info.get('prompt_tokens', 0)
            print(f"输入Token数: {input_tokens}")
            
            # 输出tokens
            output_tokens = usage_info.get('output_tokens') or usage_info.get('completion_tokens', 0)
            print(f"输出Token数: {output_tokens}")
            
            # 总计tokens
            total_tokens = usage_info.get('total_tokens', input_tokens + output_tokens)
            print(f"总Token数: {total_tokens}")
            
            # # 思考tokens (如果有的话，主要用于OpenAI o1系列模型)
            # reasoning_tokens = usage_info.get('reasoning_tokens') or usage_info.get('cached_tokens', 0)
            # if reasoning_tokens > 0:
            #     print(f"思考Token数: {reasoning_tokens}")
            
            # 缓存tokens (如果有的话)
            cached_tokens = usage_info.get('cached_tokens', 0)
            if cached_tokens > 0:
                print(f"缓存Token数: {cached_tokens}")
                
            print(f"===============================\n")
            
        else:
            print(f"\n=== {context_name} ===")
            print("未找到Token使用信息")
            print("===============================\n")
            
    except Exception as e:
        print(f"\n=== {context_name} ===")
        print(f"获取Token使用信息时出错: {str(e)}")
        print("===============================\n")


def print_detailed_response_info(response, context_name="LLM调用"):
    """
    打印详细的响应信息，包括所有可用的元数据
    
    Args:
        response: LLM响应对象
        context_name: 调用上下文名称
    """
    print(f"\n=== {context_name} 详细响应信息 ===")
    
    # 基本属性
    if hasattr(response, 'content'):
        content_length = len(str(response.content))
        print(f"响应内容长度: {content_length} 字符")
    
    # response_metadata
    if hasattr(response, 'response_metadata'):
        print(f"response_metadata: {response.response_metadata}")
    
    # usage_metadata
    if hasattr(response, 'usage_metadata'):
        print(f"usage_metadata: {response.usage_metadata}")
    
    # additional_kwargs
    if hasattr(response, 'additional_kwargs'):
        print(f"additional_kwargs: {response.additional_kwargs}")
        
    print("=====================================\n")
    
    # 调用token使用信息打印
    print_token_usage(response, context_name)
