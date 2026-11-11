"""Misión 10: RAG docente con Chroma, TF-IDF offline y Gemini opcional."""
import argparse, csv, os, re, shutil
from pathlib import Path
import chromadb
from dotenv import load_dotenv
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

BASE=Path(__file__).resolve().parents[1]
DATA=BASE/'data'
DB=BASE/'.chroma'
COLLECTION='nebulalab'
load_dotenv(BASE/'.env')

def load_docs():
    docs=[]
    for path in sorted(DATA.iterdir()):
        if path.suffix.lower()=='.txt':
            txt=path.read_text(encoding='utf-8')
            docs.append((path.name,txt))
        elif path.suffix.lower()=='.pdf':
            reader=PdfReader(str(path))
            for n,page in enumerate(reader.pages,1):
                txt=page.extract_text() or ''
                if txt.strip(): docs.append((f'{path.name} (pág. {n})',txt))
    return docs

def chunks(text,size=650,overlap=100):
    if size<=overlap: raise ValueError('size debe superar overlap')
    text=re.sub(r'\s+',' ',text).strip()
    if not text: return []
    return [text[i:i+size] for i in range(0,len(text),size-overlap) if text[i:i+size].strip()]

def backend(): return os.getenv('EMBEDDING_BACKEND','tfidf').lower()

def gemini_embed(texts,task):
    from google import genai
    from google.genai import types
    client=genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    model=os.getenv('GEMINI_EMBEDDING_MODEL','gemini-embedding-001')
    output=[]
    for text in texts:
        r=client.models.embed_content(model=model,contents=text,config=types.EmbedContentConfig(task_type=task))
        output.append(list(r.embeddings[0].values))
    return normalize(output).tolist()

def make_vectors(texts,fit=False):
    if backend()=='gemini': return gemini_embed(texts,'RETRIEVAL_DOCUMENT' if fit else 'RETRIEVAL_QUERY')
    from joblib import dump,load
    path=BASE/'.tfidf.joblib'
    if fit:
        v=TfidfVectorizer(ngram_range=(1,2),strip_accents='unicode',lowercase=True,sublinear_tf=True)
        arr=v.fit_transform(texts)
        dump(v,path)
    else:
        if not path.exists(): raise RuntimeError('Ejecuta primero index')
        arr=load(path).transform(texts)
    return arr.toarray().tolist()

def index(size=650,overlap=100):
    docs=load_docs()
    items=[(f'{name}#chunk{i+1}',name,chunk) for name,text in docs for i,chunk in enumerate(chunks(text,size,overlap))]
    if not items: raise RuntimeError('No hay documentos en data/')
    if DB.exists(): shutil.rmtree(DB)
    client=chromadb.PersistentClient(path=str(DB))
    col=client.get_or_create_collection(COLLECTION,metadata={'hnsw:space':'cosine'})
    vectors=make_vectors([it[2] for it in items],fit=True)
    col.add(ids=[x[0] for x in items],documents=[x[2] for x in items],metadatas=[{'source':x[1],'embedding_backend':backend()} for x in items],embeddings=vectors)
    print(f'Indexados {len(items)} fragmentos de {len(docs)} documentos. Backend: {backend()}')

def retrieve(question,k=3):
    client=chromadb.PersistentClient(path=str(DB))
    col=client.get_collection(COLLECTION)
    if col.count()==0: raise RuntimeError('Índice vacío. Ejecuta index')
    qvec=make_vectors([question],fit=False)[0]
    out=col.query(query_embeddings=[qvec],n_results=min(k,col.count()),include=['documents','metadatas','distances'])
    return [{'id':f'F{i+1}','source':m['source'],'text':d,'distance':round(float(dist),3)} for i,(d,m,dist) in enumerate(zip(out['documents'][0],out['metadatas'][0],out['distances'][0]))]

def answer(question,gemini=False,k=3):
    sources=retrieve(question,k)
    print('\nFUENTES RECUPERADAS:')
    for s in sources: print(f"[{s['id']}] {s['source']} (distancia {s['distance']})\n  {s['text'][:230]}...")
    if not gemini:
        print('\nMODO LOCAL (extractivo, no LLM): lee los fragmentos citados y formula tu respuesta; comprueba la vigencia documental.')
        return sources
    from google import genai
    client=genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    context='\n\n'.join(f"[{s['id']}] {s['source']}\n{s['text']}" for s in sources)
    prompt=("Eres un asistente de políticas internas. Responde solo con el contexto. "
            "Cita [F1], [F2], etc. en cada afirmación relevante. "
            "Si falta información, indícalo. Si hay documentos contradictorios, "
            "identifica el conflicto, da prioridad a documentos vigentes y no ejecutes acciones.\n\n"
            f"CONTEXTO:\n{context}\n\nPREGUNTA: {question}")
    response=client.models.generate_content(model=os.getenv('GEMINI_MODEL','gemini-2.5-flash'),contents=prompt)
    print('\nRESPUESTA GEMINI:\n'+str(response.text))
    return sources

def evaluate(path,k=3):
    with open(path,encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    n=0; hits=0;rr=0.0
    for row in rows:
        if not row.get('fuente_esperada'): continue
        n+=1; got=retrieve(row['pregunta'],k)
        ranks=[i+1 for i,s in enumerate(got) if row['fuente_esperada'] in s['source']]
        rank=min(ranks) if ranks else 0
        hits+=bool(rank);rr+=(1/rank if rank else 0)
        print(f"{'OK' if rank else 'FALLO'} | rank={rank} | {row['pregunta']}")
    print(f'Hit@{k}: {hits}/{n} = {hits/n:.1%}; MRR@{k}: {rr/n:.3f}' if n else 'Sin filas evaluables')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest='cmd',required=True)
    i=sub.add_parser('index');i.add_argument('--size',type=int,default=650);i.add_argument('--overlap',type=int,default=100)
    a=sub.add_parser('ask');a.add_argument('question');a.add_argument('--gemini',action='store_true');a.add_argument('-k',type=int,default=3)
    e=sub.add_parser('evaluate');e.add_argument('--file',required=True);e.add_argument('-k',type=int,default=3)
    args=p.parse_args()
    try:
        if args.cmd=='index': index(args.size,args.overlap)
        elif args.cmd=='ask': answer(args.question,args.gemini,args.k)
        else: evaluate(args.file,args.k)
    except (KeyError,FileNotFoundError) as ex:
        p.error(f'Configuración o fichero ausente: {ex}')
