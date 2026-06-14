from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, AsyncSessionLocal
from app.schemas.analysis import ChatMessageRequest
from app.services.chat_service import chat_service
from app.models.analysis import ChatMessage, ChatRole
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("")
async def stream_chat(request: ChatMessageRequest, db: AsyncSession = Depends(get_db)):
    """
    Accepts a message, retrieves RAG context from Qdrant, and streams the response using SSE.
    """
    # 1. Save User Message to DB
    user_msg = ChatMessage(
        analysis_id=request.analysis_id,
        role=ChatRole.user,
        content=request.message
    )
    db.add(user_msg)
    await db.commit()

    # 2. Create the generator for Server-Sent Events (SSE)
    async def sse_generator():
        full_response = ""
        
        try:
            async for token in chat_service.generate_chat_stream(
                str(request.analysis_id), 
                request.message, 
                request.history
            ):
                full_response += token
                # Yield in SSE format
                # We replace newlines so they don't break the SSE format natively,
                # or we just send valid JSON chunks
                data_payload = json.dumps({"token": token})
                yield f"data: {data_payload}\n\n"
                
        except Exception as e:
            print(f"Chat streaming error: {e}")
            yield f"data: {json.dumps({'token': '[ERROR]'})}\n\n"

        yield "data: [DONE]\n\n"
        
        # 3. Save Assistant Message to DB after streaming completes
        if full_response:
            async with AsyncSessionLocal() as session:
                ai_msg = ChatMessage(
                    analysis_id=request.analysis_id,
                    role=ChatRole.assistant,
                    content=full_response
                )
                session.add(ai_msg)
                await session.commit()

    return StreamingResponse(sse_generator(), media_type="text/event-stream")
