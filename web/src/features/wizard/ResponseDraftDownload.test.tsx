import {fireEvent,render,screen} from '@testing-library/react';
import {test,vi} from 'vitest';
import {ResponseDraftDownload} from './ResponseDraftDownload';
import type {ApiClient} from '../../infrastructure/api';
test('never saves bytes when their SHA differs from the exact reviewed document',async()=>{
 const blob={size:8,arrayBuffer:async()=>new TextEncoder().encode('modified').buffer} as Blob;
 const api={downloadResponseDraft:vi.fn().mockResolvedValue(blob)} as unknown as ApiClient;
 const scope='owner/pkg';render(<ResponseDraftDownload api={api} scopeKey={scope} packageId="pkg" draft={{draft_id:'docx',version:1,content_format:'DOCX',content_sha256:'a'.repeat(64)}}/>);
 fireEvent.click(screen.getByRole('button',{name:'Télécharger la pièce exacte'}));
 await screen.findByText(/SHA-256 discordant/);
});
