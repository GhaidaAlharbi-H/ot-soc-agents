from pydantic import BaseModel, ConfigDict
from core.llm import chat, chat_structured

class ModbusFunction(BaseModel):
    model_config = ConfigDict(extra="forbid")  # strict mode needs additionalProperties: false
    code: int
    name: str
    is_write: bool
    explanation: str

def main():
    msg = chat([{"role": "user", "content": "In one sentence: what is Modbus/TCP?"}])
    print("PLAIN:\n", msg.content, "\n")

    fact = chat_structured(
        [
            {"role": "system", "content": "You are an ICS protocol expert. State only accurate facts."},
            {"role": "user", "content": "Describe Modbus function code 16."},
        ],
        ModbusFunction,
    )
    print("STRUCTURED:\n", fact.model_dump_json(indent=2))
    assert fact.code == 16 and fact.is_write, "Wrong answer: check the trace."

if __name__ == "__main__":
    main()