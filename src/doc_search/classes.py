import dataclasses
@dataclasses.dataclass
class Chunks:
    chunks: list

    def save_to_txt(self, filename):
        with open(filename, "w") as file:
            for chunk in self.chunks:
                file.write(chunk.text + "\n")
                file.write(chunk.url + "\n")
                file.write("-"*100)

    @classmethod
    def from_file(cls, filename):
        with open(filename,"r") as file:




@dataclasses.dataclass
class TextChunk:
    text: str
    url: str

    def __str__(self):
        return self.text
    
    def __len__(self):
        return len(self.text)

 