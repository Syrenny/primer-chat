import 'katex/dist/katex.min.css'
import React from 'react'
import ReactMarkdown from 'react-markdown'
import rehypeHighlight from 'rehype-highlight'
import rehypeKatex from 'rehype-katex'
import rehypeRaw from 'rehype-raw'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import { components } from './components'

const codeLanguageSubset = [
	'python',
	'javascript',
	'java',
	'go',
	'bash',
	'c',
	'cpp',
	'csharp',
	'css',
	'diff',
	'graphql',
	'json',
	'kotlin',
	'less',
	'lua',
	'makefile',
	'markdown',
	'objectivec',
	'perl',
	'php',
	'php-template',
	'plaintext',
	'python-repl',
	'r',
	'ruby',
	'rust',
	'scss',
	'shell',
	'sql',
	'swift',
	'typescript',
	'vbnet',
	'wasm',
	'xml',
	'yaml',
]

interface MarkdownRendererProps {
	content: string
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
	return (
		<div className='markdown break-words w-full max-w-full overflow-hidden text-foreground font-sans text-base leading-relaxed'>
			<ReactMarkdown
				remarkPlugins={[
					remarkGfm,
					[remarkMath, { singleDollarTextMath: true }],
				]}
				rehypePlugins={[
					rehypeKatex,
					rehypeRaw,
					[
						rehypeHighlight,
						{
							detect: true,
							ignoreMissing: true,
							subset: codeLanguageSubset,
						},
					],
				]}
				skipHtml={false}
				components={components}
			>
				{content}
			</ReactMarkdown>
		</div>
	)
}

export default MarkdownRenderer
